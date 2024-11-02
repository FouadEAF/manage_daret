from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    user_source_username = serializers.ReadOnlyField(
        source='user_source.username')
    user_destination_username = serializers.ReadOnlyField(
        source='user_destination.username')

    class Meta:
        model = Notification
        fields = ['id', 'user_source', 'user_source_username', 'user_destination',
                  'user_destination_username', 'message', 'created_at', 'is_read']
        read_only_fields = ['user_source',
                            'user_source_username', 'created_at', 'is_read']
