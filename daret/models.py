from django.db import models
from users.models import User


class Daret(models.Model):
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='darets')
    name = models.CharField(max_length=50)
    date_start = models.DateField()
    mensuel = models.IntegerField()
    is_part = models.BooleanField(default=False)
    nbre_elements = models.IntegerField(default=0)
    is_done = models.BooleanField(default=False)
    codeGroup = models.CharField(max_length=20, unique=True)


class JoinDaret(models.Model):
    daret = models.ForeignKey(
        Daret, on_delete=models.CASCADE, related_name='joinDarets')
    participant = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='joinDarets')
    is_confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
