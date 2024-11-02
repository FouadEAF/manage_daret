from .models import User  # Assuming you have a custom User model
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User
from django.contrib.auth.models import Group


class UserUpdateForm(UserChangeForm):
    """ Form to update user information """
    is_superuser = forms.BooleanField(
        label='Superuser status', required=False, initial=False)
    is_staff = forms.BooleanField(
        label='Staff status', required=False, initial=False)
    # role = forms.CharField(max_length=50, required=True)
    birthday = forms.DateField(required=False, widget=forms.SelectDateWidget)
    phone = forms.CharField(max_length=20, required=False)
    bank_account = forms.CharField(max_length=30, required=False)

    class Meta(UserChangeForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'birthday', 'phone',
                  'cnie', 'bank_account', 'is_superuser', 'is_staff')

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields['username'].required = False
            self.fields['username'].validators = []

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_superuser = self.cleaned_data.get('is_superuser', False)
        user.is_staff = self.cleaned_data.get('is_staff', False)

        if commit:
            user.save()

        # role = self.cleaned_data.get('role')
        # if role:
        #     group, _ = Group.objects.get_or_create(name=role)
        #     user.groups.add(group)

        return user


class SignUpForm(UserCreationForm):
    """Form to create a new user"""
    is_superuser = forms.BooleanField(
        label='Superuser status', required=False, initial=False)
    is_staff = forms.BooleanField(
        label='Staff status', required=False, initial=False)
    birthday = forms.DateField(required=False, widget=forms.SelectDateWidget)
    phone = forms.CharField(max_length=20, required=False)
    bank_account = forms.CharField(max_length=30, required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'birthday', 'phone',
                  'cnie', 'bank_account', 'is_superuser', 'is_staff')

    # def clean_bank_account(self):
    #     bank_account = self.cleaned_data.get('bank_account')
    #     if bank_account and User.objects.filter(bank_account=bank_account).exists():
    #         raise forms.ValidationError("This bank account already exists.")
    #     return bank_account
    def clean(self):
        cleaned_data = super().clean()
        bank_account = cleaned_data.get('bank_account')

        if bank_account and User.objects.filter(bank_account=bank_account).exists():
            self.add_error('bank_account', "This bank account already exists.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_superuser = self.cleaned_data.get('is_superuser', False)
        user.is_staff = self.cleaned_data.get('is_staff', False)

        if commit:
            user.save()

        # Uncomment this if you're using role-based groups
        # role = self.cleaned_data.get('role')
        # if role:
        #     group, _ = Group.objects.get_or_create(name=role)
        #     user.groups.add(group)

        return user


class UserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name',
                  'birthday', 'phone', 'cnie', 'bank_account')
