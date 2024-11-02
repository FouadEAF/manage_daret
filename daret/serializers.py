
from rest_framework import serializers

from users.models import User
from .models import Daret, JoinDaret


class DaretSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Daret
        fields = ['id', 'owner', 'full_name', 'name', 'date_start',
                  'mensuel', 'nbre_elements', 'is_part', 'is_done', 'codeGroup']

    def get_full_name(self, obj):
        """Get full name for the owner."""
        if obj.owner:
            return f"{obj.owner.first_name} {obj.owner.last_name}"
        return None


class JoinDaretSerializer(serializers.ModelSerializer):
    participant_name = serializers.CharField(
        source='participant.username', read_only=True
    )

    daret_name = serializers.CharField(
        source='daret.name', read_only=True
    )
    participant_full_name = serializers.SerializerMethodField()

    class Meta:
        model = JoinDaret
        fields = ['id', 'daret', 'daret_name', 'participant',
                  'participant_name', 'participant_full_name', 'is_confirmed', 'created_at']

    def get_participant_full_name(self, obj):
        """Get full name for the user."""
        if obj.participant:
            return f"{obj.participant.first_name} {obj.participant.last_name}"
        return None
