from django.conf import settings
from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView

from TastyIdeas.accounts import forms as account_forms
from TastyIdeas.accounts.models import EmailVerification, User
from TastyIdeas.accounts.tasks import send_verification_email
from TastyIdeas.common.urls import get_referer_or_default
from TastyIdeas.common.views import LogoutRequiredMixin, TitleMixin
from TastyIdeas.utils.uid import is_valid_uuid


class UserRegistrationView(LogoutRequiredMixin, SuccessMessageMixin, TitleMixin, CreateView):
    model = User
    form_class = account_forms.UserRegistrationForm
    template_name = 'accounts/registration.html'
    success_message = 'Registration successful!'
    success_url = reverse_lazy('accounts:login')
    title = 'Tasty | Registration'


class UserLoginView(LogoutRequiredMixin, TitleMixin, auth_views.LoginView):
    form_class = account_forms.UserLoginForm
    template_name = 'accounts/login.html'
    title = 'Tasty | Registration'

    def get(self, request, *args, **kwargs):
        request.session['before_login_url'] = get_referer_or_default(self.request, None)
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        next_query = self.request.session.get('before_login_url')
        return next_query if next_query else reverse_lazy('accounts:profile', args={self.request.user.slug})

    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')
        if not remember_me:
            self.request.session.set_expiry(0)
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, 'Invalid data entered. Please try again.')
        return super().form_invalid(form)


class LogoutView(auth_views.LogoutView):
    def get_redirect_url(self):
        next_page = get_referer_or_default(self.request)
        return next_page


class UserProfileView(SuccessMessageMixin, TitleMixin, UpdateView):
    model = User
    form_class = account_forms.UserProfileForm
    template_name = 'accounts/profile/profile.html'
    title = 'Tasty | Account'
    success_message = 'Profile updated successfully!'

    def get_success_url(self):
        return reverse_lazy('accounts:profile', args=(self.object.slug,))

    def form_invalid(self, form):
        self.object.refresh_from_db()
        return super().form_invalid(form)


class UserProfilePasswordView(SuccessMessageMixin, auth_views.PasswordChangeView):
    form_class = account_forms.PasswordChangeForm
    template_name = 'accounts/profile/profile.html'
    title = 'Tasty | Password'
    success_message = 'Password updated successfully!'

    def get_success_url(self):
        return reverse_lazy('accounts:profile-password', args={self.request.user.slug})


class UserProfileEmailView(SuccessMessageMixin, auth_views.PasswordChangeView):
    form_class = account_forms.EmailChangeForm
    template_name = 'accounts/profile/profile.html'
    title = 'Tasty | Email'
    success_message = 'Email updated successfully!'

    def get_success_url(self):
        return reverse_lazy('accounts:profile-email', args={self.request.user.slug})


class SendVerificationEmailView(LoginRequiredMixin, TitleMixin, TemplateView):
    template_name = 'accounts/email/email_verification_done.html'
    title = 'Tasty| Send Verification'
    sending_interval = settings.EMAIL_SEND_INTERVAL_SECONDS

    def get(self, request, *args, **kwargs):
        email = kwargs.get('email')
        user = get_object_or_404(User, email=email)

        if not user.is_request_user_matching(request):
            raise Http404

        seconds_since_last_email = user.seconds_since_last_email_verification()

        if user.is_verified:
            messages.warning(request, 'Your email is already verified.')
        elif seconds_since_last_email < self.sending_interval:
            seconds_left = self.sending_interval - seconds_since_last_email
            messages.warning(request, f'Please wait {seconds_left} to resend the confirmation email.')
        else:
            verification = user.create_email_verification()
            send_verification_email.delay(verification.id)
        return super().get(request, *args, **kwargs)


class EmailVerificationView(TemplateView):
    template_name = 'accounts/email/email_verification_complete.html'

    def get(self, request, *args, **kwargs):
        code = kwargs.get('code')
        email = kwargs.get('email')
        user = get_object_or_404(User, email=email)

        if not user.is_request_user_matching(request) or not is_valid_uuid(str(code)):
            raise Http404

        verification = get_object_or_404(EmailVerification, user=user, code=code)

        if user.is_verified:
            messages.warning(request, 'Your email is already verified.')
        elif not verification.is_expired():
            user.verify()
        else:
            messages.warning(request, 'The verification link has expired.')
        return super().get(request, *args, **kwargs)


class PasswordResetView(LogoutRequiredMixin, SuccessMessageMixin, auth_views.PasswordResetView):
    title = 'Tasty | Password Reset'
    template_name = 'accounts/password/reset_password.html'
    subject_template_name = 'accounts/password/password_reset_subject.html'
    email_template_name = 'accounts/password/password_reset_email.html'
    form_class = account_forms.PasswordResetForm
    success_url = reverse_lazy('accounts:reset_password')
    success_message = 'We’ve emailed you instructions for setting your password. ' \
                      'You should receive them shortly. If you don’t receive an email, ' \
                      'please check your spam folder.'


class PasswordResetConfirmView(LogoutRequiredMixin, SuccessMessageMixin, TitleMixin,
                               auth_views.PasswordResetConfirmView):
    title = 'Tasty | Password Reset'
    template_name = 'accounts/password/password_reset_confirm.html'
    form_class = account_forms.SetPasswordForm
    success_url = reverse_lazy('accounts:login')
    success_message = 'Your password has been set successfully. You can now sign in to your account.'
