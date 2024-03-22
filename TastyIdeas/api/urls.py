from django.urls import include, path

app_name = 'api'

urlpatterns = [
    path('', include('TastyIdeas.api.recipe.urls', namespace='recipe')),
    path('', include('TastyIdeas.api.accounts.urls', namespace='accounts')),
]