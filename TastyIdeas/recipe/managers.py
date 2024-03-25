from django.db import models
from django.db.models import Count

from TastyIdeas.common.cache import get_cached_data_or_set_new


class CategoryManager(models.Manager):
    """
    Manager for Category model.
    """

    categories_cache_time = 60 * 60  # Cache time for categories

    def cached_queryset(self):
        """
        Get queryset of categories from cache if available, otherwise fetch from database and cache it.
        """
        return get_cached_data_or_set_new('categories', self.all, self.categories_cache_time)


class RecipeManager(models.Manager):
    """
    Manager for Recipe model.
    """

    recipes_cache_time = 60 * 60  # Cache time for recipes
    popular_recipes_cache_time = 3600 * 24  # Cache time for popular recipes

    def cached_queryset(self):
        """
        Get queryset of recipes from cache if available, otherwise fetch from database and cache it.
        """
        return get_cached_data_or_set_new('recipes', self.all, self.recipes_cache_time)

    def cached_popular_recipes(self):
        """
        Get queryset of popular recipes from cache if available, otherwise fetch from database,
        annotate with bookmarks count, order by bookmarks count, and cache it.
        """
        return get_cached_data_or_set_new(
            'popular_recipes',
            lambda: self.annotate(bookmarks_count=Count('bookmarks')).order_by('-bookmarks_count'),
            self.popular_recipes_cache_time,
        )

    def user_bookmarked_recipes(self, user):
        """
        Get queryset of recipes bookmarked by the given user.
        """
        return self.filter(bookmarks=user) if user.is_authenticated else None
