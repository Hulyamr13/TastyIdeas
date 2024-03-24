from celery import shared_task
from django.conf import settings

from TastyIdeas.accounts.models import EmailVerification, User
from TastyIdeas.common.mail import convert_html_to_email_message


@shared_task
def send_verification_email(verification_id):
    """
    Task to send email verification.
    """
    verification = EmailVerification.objects.get(id=verification_id)
    verification.send_verification_email(protocol=settings.PROTOCOL)


@shared_task
def send_email(subject_template_name, email_template_name, to_email, context=None):
    """
    Task to send an email with given subject and template.
    """
    user_id = context.get('user')
    user = User.objects.get(id=user_id) if user_id else None
    if user:
        context['user'] = user
    msg = convert_html_to_email_message(subject_template_name, email_template_name, [to_email], context)
    msg.send()
