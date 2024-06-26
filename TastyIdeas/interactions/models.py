from django.db import models

from TastyIdeas.interactions.managers import RecipeBookmarkManager


class RecipeBookmark(models.Model):
    recipe = models.ForeignKey(to='recipe.Recipe', on_delete=models.CASCADE)
    user = models.ForeignKey(to='accounts.User', on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)

    objects = RecipeBookmarkManager()

    def __str__(self):
        return f'{self.user.username} | {self.recipe.name}'


class RecipeComment(models.Model):
    recipe = models.ForeignKey(to='recipe.Recipe', on_delete=models.CASCADE)
    author = models.ForeignKey(to='accounts.User', null=True, on_delete=models.SET_NULL)
    text = models.CharField(max_length=500)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text
