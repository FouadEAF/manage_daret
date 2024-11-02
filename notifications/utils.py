# utils.py (or any suitable location)
from .models import Notification


def create_notification(user_source, user_destination, message):
    """Create a notification."""
    notification = Notification.objects.create(
        user_source=user_source,
        user_destination=user_destination,
        message=message,
    )
    return notification
