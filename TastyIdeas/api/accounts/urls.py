from django.urls import include, path
from djoser.views import UserViewSet
from rest_framework import routers

from TastyIdeas.api.accounts.views import (EmailVerificationUpdateAPIView, SendVerificationEmailCreateAPIView)
from TastyIdeas.utils.urls import filter_urls

app_name = 'accounts'

djoser_router = routers.DefaultRouter()
djoser_router.register(r'users', UserViewSet, basename='users')
allowed_djoser_url_names = [
    'users-me',
    'users-detail',
    'users-list',
    'users-set-password',
    'users-reset-password',
    'users-reset-password-confirm',
]
filtered_djoser_router_urls = filter_urls(djoser_router.urls, allowed_djoser_url_names)

urlpatterns = [
    path('', include(filtered_djoser_router_urls)),
    path('auth/', include('djoser.urls.authtoken')),
    path('verification/send/', SendVerificationEmailCreateAPIView.as_view(), name='send-verification-email'),
    path('verify/', EmailVerificationUpdateAPIView.as_view(), name='email-verification'),
]