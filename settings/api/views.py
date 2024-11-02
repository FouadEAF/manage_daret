from django.http import JsonResponse


def invalid_route(request, invalid_path=None):
    return JsonResponse({'success': False, 'message': 'Invalid path'}, status=404)
