import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404

from authentication.utils import APIAccessMixin
from users.models import User
from .models import Notification
from .serializers import NotificationSerializer


class ManageNotificationView(APIAccessMixin, APIView):
    """Manage Notifications"""
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """Create a new notification"""
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return Response({'success': False, 'message': 'Invalid JSON data'}, status=400)

        # Extract necessary fields from request
        user_source = request.user  # The authenticated user is the source
        # Get the username of the destination user
        user_destination_username = data.get('user_destination')
        message = data.get('message')

        if not user_destination_username or not message:
            return Response({'success': False, 'message': 'Both user_destination and message are required.'}, status=400)

        # Fetch the user_destination by username
        try:
            user_destination = User.objects.get(
                username=user_destination_username)
        except User.DoesNotExist:
            return Response({'success': False, 'message': 'User destination does not exist.'}, status=404)

        # Create the notification
        notification = Notification.objects.create(
            user_source=user_source,
            user_destination=user_destination,  # Store the user instance, not just the ID
            message=message
        )

        return Response({'success': True, 'message': 'Notification created successfully.'}, status=201)

    def get(self, request, *args, **kwargs):
        """Retrieve all notifications for the logged-in user"""
        user = request.user

        # Fetch unread and read notifications for the user
        notifications = Notification.objects.filter(
            user_destination=user)
        unread_notifications = Notification.objects.filter(
            user_destination=user, is_read=False).count()

        serializer = NotificationSerializer(notifications, many=True)

        return Response({'success': True, 'data': serializer.data, 'unread_count': unread_notifications}, status=200)

    def put(self, request, notification_id, *args, **kwargs):
        """Mark a notification as read"""
        # Retrieve the notification
        notification = get_object_or_404(
            Notification, id=notification_id, user_destination=request.user)

        # Update the `is_read` field
        notification.is_read = True
        notification.save()

        return Response({'success': True, 'message': 'Notification marked as read.'}, status=200)

    def delete(self, request, notification_id=None, *args, **kwargs):
        """Delete a single notification or all notifications for the current user"""
        user = request.user

        if notification_id:
            # Case 1: Delete a specific notification by its ID
            notification = get_object_or_404(
                Notification, id=notification_id, user_destination=user)
            notification.delete()
            return Response({'success': True, 'message': 'Notification deleted successfully.'}, status=200)
        else:

            # Case 2: Delete all notifications for the current user
            deleted_count, _ = Notification.objects.filter(
                user_destination=user).delete()
            return Response({'success': True, 'message': f'All {deleted_count} notifications deleted successfully.'}, status=200)
