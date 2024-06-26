from django.conf import settings
from rest_framework.pagination import PageNumberPagination


class CategoryPageNumberPagination(PageNumberPagination):
    page_size = settings.CATEGORIES_PAGINATE_BY
    page_size_query_param = 'page_size'
    max_page_size = 48


class RecipePageNumberPagination(PageNumberPagination):
    page_size = settings.RECIPES_PAGINATE_BY
    page_size_query_param = 'page_size'
    max_page_size = 32


class CommentPageNumberPagination(PageNumberPagination):
    page_size = settings.COMMENTS_PAGINATE_BY
    page_size_query_param = 'page_size'
    max_page_size = 12