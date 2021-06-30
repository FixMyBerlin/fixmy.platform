from django.conf import settings
from django.core import mail
from django.template.loader import render_to_string


def send_double_opt_in(signup):
    """Send email with a double opt-in link for the newsletter."""
    context = {"signup": signup}
    subject = "Bitte bestätigen Sie, dass sie Neuigkeiten von der Infostelle Fahrradparken erhalten möchten"
    body = render_to_string('notice_opt_in.txt', context=context)
    mail.send_mail(subject, body, settings.DEFAULT_FROM_EMAIL)