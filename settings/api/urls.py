from django.urls import path, include, re_path
from . import views

app_name = 'api'

urlpatterns = [
    path('auth/', include('authentication.urls')),
    path('daret/', include('daret.urls')),
    path('tour/', include('tour.urls')),
    path('notifications/', include('notifications.urls')),

    # Catch-all route for invalid paths within api/v1/
    re_path(r'^(?P<invalid_path>.*)$', views.invalid_route),
]
