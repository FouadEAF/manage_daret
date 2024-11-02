from django.urls import path
from .views import ManageNotificationView


urlpatterns = [
    path('', ManageNotificationView.as_view()),
    path('<str:notification_id>', ManageNotificationView.as_view()),
]
