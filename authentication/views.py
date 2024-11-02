from django.utils.timezone import now
from django.forms.models import model_to_dict

from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework.authentication import SessionAuthentication
from datetime import timedelta
import json
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.hashers import check_password
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from users.forms import SignUpForm, UserUpdateForm
from users.models import User
from authentication.utils import APIAccessMixin, get_tokens_for_user


class CreateUser(APIView):
    """ Create new user """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return Response({'success': False, 'message': 'Invalid JSON'}, status=400)

        form = SignUpForm(data)
        if form.is_valid():
            user = form.save()
            user.backend = 'users.authentication.UserBackend'
            return Response({'success': True, 'message': 'User created successfully'}, status=201)
        else:
            return Response({'success': False, 'message': form.errors}, status=400)


class UpdateUser(APIAccessMixin, APIView):
    """ Update information of user """
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cnie = data.get('cnie')
            if not cnie:
                return Response({'success': False, 'message': 'CNIE is required'}, status=400)
        except json.JSONDecodeError:
            return Response({'success': False, 'message': 'Invalid JSON data'}, status=400)

        try:
            user = User.objects.get(cnie=cnie)
        except User.DoesNotExist:
            return Response({'success': False, 'message': 'User not found'}, status=404)

        data['password1'] = data['password2'] = user.password

        form = UserUpdateForm(data, instance=user)
        if form.is_valid():
            updated_user = form.save()
            return Response({'success': True, 'message': 'User updated successfully'}, status=200)
        else:
            return Response({'success': False, 'message': form.errors}, status=400)


class LoginView(APIView):
    """Login to server Backend"""
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
        except json.JSONDecodeError:
            return Response({'success': False, 'message': 'Invalid JSON data'}, status=400)

        if not username or not password:
            return Response({'success': False, 'message': 'Username and password are required.'}, status=400)

        # Authenticate user with username
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_active:
            # Login the user
            auth_login(request, user)

            # Generate tokens
            tokens = get_tokens_for_user(user)

            # Define the expiration time for refresh and access tokens
            refresh_token_lifetime = now() + timedelta(days=7)
            access_token_lifetime = now() + timedelta(minutes=60)

            # Serialize user data
            response_data = {
                'success': True,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'cnie': user.cnie,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'isActive': user.is_active,
                },
                'refresh_token': tokens['refresh'],
                'access_token': tokens['access'],
            }

            response = Response(response_data, status=200)

            # Set cookies for tokens
            response.set_cookie(
                key='refresh_token',
                value=tokens['refresh'],
                httponly=True,
                secure=True,
                samesite='Lax',
                expires=refresh_token_lifetime,
            )

            response.set_cookie(
                key='access_token',
                value=tokens['access'],
                httponly=True,
                secure=True,
                samesite='Lax',
                expires=access_token_lifetime,
            )

            # Set CORS headers
            response["Access-Control-Allow-Origin"] = "http://localhost:8000"
            response["Access-Control-Allow-Credentials"] = "true"

            return response
        else:
            return Response({'success': False, 'message': 'Invalid credentials'}, status=401)


class LogoutView(APIAccessMixin, APIView):
    """ Logout from the server backend """
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            auth_logout(request)

            response = Response(
                {'success': True, 'message': 'Logout successful'}, status=200)

            response.delete_cookie('refresh_token')
            response.delete_cookie('access_token')
            response.delete_cookie('csrftoken')
            response.delete_cookie('sessionid')

            return response

        else:
            return Response({'success': False, 'message': 'Authentication Required'}, status=401)


class AboutMeView(APIAccessMixin, APIView):
    """About me - get all information about user"""
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({'success': False, 'message': 'User is not authenticated'}, status=401)

        user = request.user
        user_data = model_to_dict(user),
        # user_data = {
        #     'idUser': user.id,
        #     'username': user.username,
        #     'cnie': user.cnie,

        #     'isActive': user.is_active,

        # }
        return Response({'success': True, 'data': user_data}, status=200)


class ChangePasswordView(APIAccessMixin, APIView):
    """ Change the password of connected user """
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            current_password = data.get('current_password')
            new_password = data.get('new_password')
            new_password_confirm = data.get('new_password_confirm')
        except json.JSONDecodeError:
            return Response({'success': False, 'message': 'Invalid JSON'}, status=400)

        user = request.user

        if not current_password or not new_password or not new_password_confirm:
            return Response({'success': False, 'message': 'All fields are required'}, status=400)

        if not check_password(current_password, user.password):
            return Response({'success': False, 'message': 'Current password is incorrect'}, status=400)

        if new_password != new_password_confirm:
            return Response({'success': False, 'message': 'New passwords do not match'}, status=400)

        user.set_password(new_password)
        user.save()

        return Response({'success': True, 'message': 'Password changed successfully'}, status=200)


class PasswordReset(APIView):
    """Reset password using CNIE."""
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cnie = data.get('cnie')
            new_password = data.get('new_password')
            confirm_password = data.get('confirm_password')
        except json.JSONDecodeError:
            return Response({'success': False, 'message': 'Invalid JSON'}, status=400)

        user = User.objects.filter(cnie=cnie).first()
        if user is None:
            return Response({'success': False, 'message': 'User not found'}, status=404)

        if new_password != confirm_password:
            return Response({'success': False, 'message': 'New passwords do not match'}, status=400)

        user.set_password(new_password)
        user.save()

        return Response({'success': True, 'message': 'Password reset successfully'}, status=200)


class RefreshTokenView(APIAccessMixin, APIView):
    """Refresh token"""
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            refresh = data.get('refresh_token')
        except json.JSONDecodeError:
            return Response({'success': False, 'message': 'Invalid JSON'}, status=400)

        if refresh is None:
            return Response({'success': False, 'message': "Refresh token is required"}, status=400)

        try:

            # Use the refresh token to issue new access and refresh tokens
            new_refresh_token = RefreshToken(refresh)
            new_access_token = new_refresh_token.access_token

            # Token lifetimes
            refresh_token_lifetime = now() + timedelta(days=7)
            access_token_lifetime = now() + timedelta(minutes=60)

            response_data = {
                'success': True,
                'access_token': str(new_access_token),
                'refresh_token': str(new_refresh_token),
            }

            response = Response(response_data, status=200)

            # Set cookies for access and refresh tokens
            response.set_cookie(
                key='refresh_token',
                value=str(new_refresh_token),
                httponly=True,
                secure=True,
                samesite='Lax',
                expires=refresh_token_lifetime,
            )

            response.set_cookie(
                key='access_token',
                value=str(new_access_token),
                httponly=True,
                secure=True,
                samesite='Lax',
                expires=access_token_lifetime,
            )

            return response

        except TokenError:
            return Response({'success': False, 'message': "Refresh token is expired or invalid"}, status=400)
        except InvalidToken:
            return Response({'success': False, 'message': "Invalid token"}, status=400)
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=400)
