import logging
from datetime import timedelta
from uuid import uuid4

from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.timezone import now

from TastyIdeas.accounts.managers import EmailVerificationManager
from TastyIdeas.common.mail import convert_html_to_email_message

logger = logging.getLogger('mailings')


class User(AbstractUser):
    image = models.ImageField(upload_to='user_images', null=True, blank=True)
    email = models.EmailField(db_index=True, unique=True, max_length=254)
    is_verified = models.BooleanField(default=False)
    slug = models.SlugField(unique=True)
    groups = models.ManyToManyField(
        to=Group,
        related_name='custom_user_groups',
        blank=True,
        verbose_name='groups',
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
    )
    user_permissions = models.ManyToManyField(
        to=Permission,
        related_name='custom_user_permissions',
        blank=True,
        verbose_name='user permissions',
        help_text='Specific permissions for this user.',
        related_query_name='user',
    )

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.username)
        try:
            super().save(*args, **kwargs)
        except ValidationError as e:
            logger.error(f"Error saving user {self.username}: {e}")

    def clean(self):
        self.email = self.email.lower()
        return super().clean()

    def seconds_since_last_email_verification(self):
        valid_verifications = EmailVerification.objects.valid_user_verifications(user=self).order_by('-created')
        if valid_verifications.exists():
            elapsed_time = now() - valid_verifications.first().created
            return elapsed_time.total_seconds()
        else:
            return settings.EMAIL_SEND_INTERVAL_SECONDS

    def create_email_verification(self):
        expiration = now() + timedelta(hours=settings.EMAIL_EXPIRATION_HOURS)
        code = uuid4()
        try:
            return EmailVerification.objects.create(code=code, user=self, expiration=expiration)
        except Exception as e:
            logger.error(f"Error creating email verification for {self.email}: {e}")

    def is_request_user_matching(self, request):
        return self == request.user

    def verify(self):
        self.is_verified = True
        self.save()


class EmailVerification(models.Model):
    code = models.UUIDField(unique=True)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    expiration = models.DateTimeField()

    objects = EmailVerificationManager()

    def __str__(self):
        return f'Email verification for {self.user.email}'

    def send_verification_email(self, subject_template_name='accounts/email/email_verification_subject.html',
                                html_email_template_name='accounts/email/email_verification_email.html',
                                protocol='http'):
        link = reverse('accounts:email-verification', kwargs={'email': self.user.email, 'code': self.code})

        context = {
            'user': self.user,
            'protocol': protocol,
            'verification_link': link,
        }
        msg = convert_html_to_email_message(subject_template_name, html_email_template_name, [self.user.email], context)
        msg.send()

        logger.info(f'Successfully sent a verification email to {self.user.email}')

    def is_expired(self):
        return self.expiration < now()
