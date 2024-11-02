from django.urls import path
from .views import ManageTourView, ManageConfirmVirementView, CardTourView


urlpatterns = [
    path('', ManageTourView.as_view()),
    path('<int:id_tour>', ManageTourView.as_view()),
    path('card', CardTourView.as_view()),
    path('confirm-virements', ManageConfirmVirementView.as_view()),
    path('confirm-virements/<int:id_confirm_virement>',
         ManageConfirmVirementView.as_view()),
]
