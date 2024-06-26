import logging

from django import forms
from django.contrib.auth import forms as auth_forms
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from TastyIdeas.accounts.models import User
from TastyIdeas.accounts.tasks import send_email

mailings_logger = logging.getLogger('mailings')
accounts_logger = logging.getLogger('accounts')


class UserRegistrationForm(auth_forms.UserCreationForm):
    username = forms.CharField(min_length=4, max_length=32, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter Username',
    }))
    email = forms.CharField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter Email',
    }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter Password',
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Confirm Password',
    }))

    def save(self, commit=True):
        username = self.data.get('username')
        accounts_logger.info(f'User {username} has registered.')
        return super().save(commit=commit)

    def clean_username(self):
        """CASE-SENSITIVE check to see if the username is already taken."""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError('A user with that username already exists.')
        return username

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class UserLoginForm(auth_forms.AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter Username',
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter Password',
    }))
    remember_me = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={
        'class': 'form-check-input',
    }))

    class Meta:
        model = User
        fields = ('username', 'password', 'remember_me')


class UserProfileForm(auth_forms.UserChangeForm):
    username = forms.CharField(min_length=4, max_length=32, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'type': 'text',
    }))
    first_name = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'type': 'text',
        'placeholder': 'Enter your first name',
    }))
    last_name = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'type': 'text',
        'placeholder': 'Enter your last name',
    }))
    email = forms.EmailField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'readonly': True,
    }))
    image = forms.ImageField(required=False, widget=forms.FileInput(attrs={
        'class': 'form-control',
        'type': 'file',
        'aria-label': 'Upload',
    }))

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        kwargs['initial'] = {'email': instance.email}
        super().__init__(*args, **kwargs)

    def clean_username(self):
        """CASE-SENSITIVE check to see if the username is already taken."""
        username = self.cleaned_data.get('username')
        if username.lower() != self.instance.username.lower() and User.objects.filter(username__iexact=username
                                                                                      ).exists():
            raise ValidationError('A user with that username already exists.')
        return username

    def save(self, commit=True):
        username = self.cleaned_data.get('username')
        if username:
            self.instance.slug = slugify(username)
        return super().save(commit=commit)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'image')


class PasswordChangeForm(auth_forms.PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your old password',
    }))
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your new password',
    }))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter new password confirmation',
    }))

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(user, *args, **kwargs)

    def clean(self):
        new_password1 = self.cleaned_data['new_password1']
        new_password2 = self.cleaned_data['new_password2']
        if new_password1 == new_password2 and self.user.check_password(new_password2):
            raise forms.ValidationError('The new password must be different from the old one.')
        return super().clean()

    class Meta:
        model = User
        fields = ('old_password', 'new_password1', 'new_password2')


class PasswordResetForm(auth_forms.PasswordResetForm):
    email = forms.CharField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter Email',
    }))

    def send_mail(self, subject_template_name, email_template_name, context, from_email, to_email,
                  html_email_template_name=None):
        context['user'] = context['user'].id
        send_email.delay(subject_template_name, email_template_name, to_email, context)
        mailings_logger.info(f'Request to send a password reset email to {to_email}')

    class Meta:
        model = User
        fields = ('email',)


class SetPasswordForm(auth_forms.SetPasswordForm):
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter new password',
    }))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Confirm new password',
    }))

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(user, *args, **kwargs)

    def clean_new_password2(self):
        new_password = self.cleaned_data['new_password1']
        if self.user.check_password(new_password):
            raise forms.ValidationError('The new password must be different from the old one.')
        return super().clean_new_password2()

    class Meta:
        model = User
        fields = ('new_password1', 'new_password2')


class EmailChangeForm(forms.Form):
    error_messages = {
        'password_incorrect': _('Your old password was entered incorrectly. Please enter it again.'),
    }
    new_email = forms.CharField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter Email',
    }))
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your password',
    }))

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data['old_password']
        if not self.user.check_password(old_password):
            raise ValidationError(self.error_messages['password_incorrect'], code='password_incorrect')
        return old_password

    def clean_new_email(self):
        new_email = self.cleaned_data.get('new_email')
        if self.user.email == new_email:
            raise forms.ValidationError("You're already using this email address.")
        if User.objects.filter(email=new_email).exists():
            raise forms.ValidationError("This email address is already in use. Please use a different email address.")
        return new_email

    def save(self, commit=True):
        self.user.email = self.cleaned_data['new_email']
        self.user.is_verified = False
        if commit:
            self.user.save()
        return self.user