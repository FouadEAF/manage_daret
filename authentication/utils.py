from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework.response import Response
from django.contrib.auth.mixins import AccessMixin


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    access = AccessToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(access),
    }


class APIAccessMixin(AccessMixin):
    """ Mixin to handle access to the API.
        Returns 401 Unauthorized instead of redirecting.
    """

    def handle_no_permission(self):
        return Response({'detail': 'You are not logged in yet'}, status=401)
