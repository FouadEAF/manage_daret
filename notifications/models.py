from django.db import models
from users.models import User


class Notification(models.Model):
    user_source = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='sent_notifications'
    )
    user_destination = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='received_notifications'
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification from {self.user_source.username} to {self.user_destination.username}: {self.message[:20]}"

    class Meta:
        # Order notifications by creation date, latest first
        ordering = ['-created_at']
