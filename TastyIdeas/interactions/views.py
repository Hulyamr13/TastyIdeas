from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import FormView, ListView

from TastyIdeas.common.urls import get_referer_or_default
from TastyIdeas.common.views import TitleMixin
from TastyIdeas.interactions.forms import RecipeCommentForm
from TastyIdeas.interactions.models import RecipeBookmark, RecipeComment
from TastyIdeas.recipe.models import Recipe


class BookmarksListView(LoginRequiredMixin, TitleMixin, ListView):
    """
    View for displaying user's bookmarks.
    """
    model = RecipeBookmark
    template_name = 'recipe/recipe_bookmarks.html'
    ordering = ('-created_date',)
    title = 'Tasty | Bookmarks'

    def get_queryset(self):
        """
        Return the user's bookmarks ordered by creation date.
        """
        queryset = self.model.objects.user_bookmarks(self.request.user)
        return queryset.order_by(*self.ordering)[:settings.RECIPES_PAGINATE_BY]


class AddCommentCreateView(LoginRequiredMixin, FormView):
    """
    View for adding a comment to a recipe.
    """
    model = RecipeComment
    form_class = RecipeCommentForm

    def form_valid(self, form):
        """
        Create a new comment for the recipe.
        """
        text = form.cleaned_data.get('text')
        recipe_id = self.kwargs.get('recipe_id')

        recipe = get_object_or_404(Recipe, id=recipe_id)

        RecipeComment.objects.create(text=text, author=self.request.user, recipe=recipe)
        return super().form_valid(form)

    def get_success_url(self):
        """
        Redirect to the previous page after successful form submission.
        """
        return get_referer_or_default(self.request)
