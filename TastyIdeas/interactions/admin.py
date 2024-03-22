from django.contrib import admin

from TastyIdeas.interactions.models import RecipeComment


class RecipeCommentInlineAdmin(admin.TabularInline):
    model = RecipeComment
    fields = ('text', 'created_date', 'author')
    readonly_fields = ('created_date', 'author')
    ordering = ('-created_date',)
