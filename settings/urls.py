""" URL configuration for settings project. """
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('settings.api.urls', namespace='api'))
]
