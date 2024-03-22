from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('summernote/', include('django_summernote.urls')),

    path('', include('TastyIdeas.recipe.urls', namespace='recipe')),
    path('interactions/', include('TastyIdeas.interactions.urls', namespace='interactions')),
    path('accounts/', include('TastyIdeas.accounts.urls', namespace='accounts')),
    path('api/tasty/', include('TastyIdeas.api.urls', namespace='api')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)