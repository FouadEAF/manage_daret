from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def create_user(self, username, cnie, password=None, first_name=None, last_name=None, birthday=None, phone=None, bank_account=None, **extra_fields):
        """Create and return a regular user with username, cnie, first_name, last_name, birthday, phone, and bank account."""
        if not username:
            raise ValueError(_('The username field must be set'))
        if not cnie:
            raise ValueError(_('The cnie field must be set'))

        user = self.model(
            username=username,
            first_name=first_name,
            last_name=last_name,
            cnie=cnie,
            birthday=birthday,
            phone=phone,
            bank_account=bank_account,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, cnie, password=None, first_name=None, last_name=None, birthday=None, phone=None, bank_account=None, **extra_fields):
        """Create and return a superuser with the specified fields."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(username, cnie, password, first_name, last_name, birthday, phone, bank_account, **extra_fields)


class User(AbstractUser):
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    cnie = models.CharField(max_length=15, unique=True)
    bank_account = models.CharField(max_length=30, blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['cnie']

    def __str__(self):
        return self.username
