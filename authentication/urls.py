from django.urls import path
from .views import CreateUser, PasswordReset, UpdateUser, LoginView, LogoutView, AboutMeView, ChangePasswordView, RefreshTokenView
# from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
# from django.contrib.auth import views as auth_views


urlpatterns = [
    path('registre', CreateUser.as_view()),
    path('update', UpdateUser.as_view()),
    path('login', LoginView.as_view()),
    path('logout', LogoutView.as_view()),
    path('me', AboutMeView.as_view()),
    path('change-password', ChangePasswordView.as_view()),
    path('password-reset', PasswordReset.as_view()),
    path('refresh', RefreshTokenView.as_view()),

]
