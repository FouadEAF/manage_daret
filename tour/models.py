from django.db import models, transaction
from django.db import models
from daret.models import Daret
from users.models import User


class Tour(models.Model):
    daret = models.ForeignKey(
        Daret, on_delete=models.CASCADE, related_name='tours')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='tours')
    date_obtenu = models.DateField()
    ordre = models.CharField(max_length=3)
    is_recu = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Save the instance first
        super().save(*args, **kwargs)

        # If this tour is marked as received, check all tours in the Daret
        if self.is_recu:
            if not self.daret.tours.filter(is_recu=False).exists():
                # All tours in the Daret are marked as received, mark the Daret as done
                self.daret.is_done = True
                self.daret.save()


class ConfirmVirement(models.Model):
    tour = models.ForeignKey(
        Tour, on_delete=models.CASCADE, related_name='confirm_virements')
    partie_beneficiaire = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='beneficiaire_confirm_virements')
    partie_donnenant = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='donnenant_confirm_virements')
    is_send = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Save the instance first
        super().save(*args, **kwargs)

        # If this confirmation is marked as sent, check all confirmations in the tour
        if self.is_send:
            if not self.tour.confirm_virements.filter(is_send=False).exists():
                # All confirmations for this tour are marked as sent, mark the tour as received
                self.tour.is_recu = True
                self.tour.save()
