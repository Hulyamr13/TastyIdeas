from django.db import models
from django.utils.text import slugify

from TastyIdeas.recipe.managers import CategoryManager, RecipeManager


class Category(models.Model):
    name = models.CharField(max_length=40)
    slug = models.SlugField(unique=True)

    objects = CategoryManager()

    class Meta:
        verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            num = 1
            original_slug = self.slug
            while Category.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{num}"
                num += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    image = models.ImageField(upload_to='recipe_images')
    name = models.CharField(max_length=40)
    description = models.CharField(max_length=200)
    cooking_description = models.TextField()
    category = models.ForeignKey(to=Category, on_delete=models.PROTECT)
    slug = models.SlugField(unique=True)
    bookmarks = models.ManyToManyField('accounts.User', blank=True, through='interactions.RecipeBookmark')
    views = models.PositiveBigIntegerField(default=0)

    objects = RecipeManager()

    def __str__(self):
        return self.name

    def ingredients(self):
        return self.ingredient_set.all()

    def comments(self):
        return self.recipecomment_set.all().prefetch_related('author')

    def bookmarks_count(self):
        return self.bookmarks.count()


class Ingredient(models.Model):
    name = models.CharField(max_length=500)
    recipe = models.ForeignKey(to=Recipe, on_delete=models.CASCADE)

    def __str__(self):
        return self.name