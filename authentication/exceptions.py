from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def auth_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        if response.status_code == status.HTTP_401_UNAUTHORIZED:
            response.data = {'success': False,
                             'message': 'Unauthorized to access this resource, please login first'}

    return response


class DisableCSRFMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        setattr(request, '_dont_enforce_csrf_checks', True)
        response = self.get_response(request)
        return response
