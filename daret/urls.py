from django.urls import path
from .views import ManageDaretView, ManageJoinDaretView


urlpatterns = [
    path('', ManageDaretView.as_view()),
    path('<str:id_daret>', ManageDaretView.as_view()),
    # path('confirm/<int:participant_id>', ConfirmDaret.as_view()),
    path('request/', ManageJoinDaretView.as_view()),
    path('request/<str:id_daret>', ManageJoinDaretView.as_view()),

]
