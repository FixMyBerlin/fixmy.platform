from django.conf import settings
from django.core import mail
from django.template.loader import render_to_string


def send_registration_confirmation(self, recipient, request):
    """Send a registration confirmation email notice"""
    subject = 'Ihr Antrag bei Xhain-Terrassen'
    body = render_to_string('xhain/notice_event_registered.txt', request=request)
    mail.send_mail(
        subject, body, settings.DEFAULT_FROM_EMAIL, [recipient], fail_silently=True
    )