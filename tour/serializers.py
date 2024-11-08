from rest_framework import serializers
from .models import ConfirmVirement, Tour


class TourSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(
        source='daret.owner.username', read_only=True
    )
    daret_name = serializers.CharField(
        source='daret.name', read_only=True
    )
    user_name = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()
    elements = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    bank_account = serializers.SerializerMethodField()

    class Meta:
        model = Tour
        fields = [
            'id',
            'daret',
            'daret_name',
            'owner',
            'ordre',
            'user',
            'user_name',
            'full_name',
            'date_obtenu',
            'bank_account',
            'total',
            'elements',
            'is_recu',
        ]

    def get_user_name(self, obj):
        """Get the username of the user."""
        if obj.user:
            return obj.user.username
        return None

    def get_full_name(self, obj):
        """Get full name for user."""
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}"
        return None

    def get_bank_account(self, obj):
        """Get the bank account of the user."""
        if obj.user:
            return obj.user.bank_account
        return None

    def get_total(self, obj):
        """Calculate total based on Daret's mensuel and nbre_elements."""
        return obj.daret.mensuel * obj.daret.nbre_elements if obj.daret else 0

    def get_elements(self, obj):
        """Get the number of elements in Daret if the owner exists."""
        if obj.daret:
            return obj.daret.nbre_elements
        return None


class ConfirmVirementSerializer(serializers.ModelSerializer):
    partie_beneficiaire_username = serializers.CharField(
        source='partie_beneficiaire.username', read_only=True
    )
    daret_name = serializers.CharField(
        source='tour.daret.name', read_only=True
    )
    # Updated to snake_case
    partie_beneficiaire_full_name = serializers.SerializerMethodField()
    partie_donnenant_full_name = serializers.SerializerMethodField()  # Updated to snake_case

    class Meta:
        model = ConfirmVirement
        fields = [
            'id',
            'daret_name',
            'tour',
            'partie_beneficiaire',
            'partie_beneficiaire_username',
            'partie_beneficiaire_full_name',
            'partie_donnenant',
            'partie_donnenant_full_name',
            'is_send',
        ]

    def get_partie_donnenant_full_name(self, obj):
        """Get full name for partie_donnenant."""
        if obj.partie_donnenant:
            return f"{obj.partie_donnenant.first_name} {obj.partie_donnenant.last_name}"
        return None

    def get_partie_beneficiaire_full_name(self, obj):
        """Get full name for partie_beneficiaire."""
        if obj.partie_beneficiaire:
            return f"{obj.partie_beneficiaire.first_name} {obj.partie_beneficiaire.last_name}"
        return None
