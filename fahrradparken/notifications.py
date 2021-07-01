from django.conf import settings
from django.core import mail
from django.template.loader import render_to_string

from .models import EventSignup


def send_registration_confirmation(instance):
    """Notify users who signed up for an event of news."""
    context = {"signup": instance}
    if type(instance) is EventSignup:
        subject = "Automatische E-Mail nach Registrierung"
        body = render_to_string('notice_registration_event.txt', context=context)
    else:
        subject = "Automatische E-Mail nach Buchung Termin Infoveranstaltung"
        body = render_to_string('notice_registration.txt', context=context)
    recipient = instance.email
    email = mail.EmailMessage(subject, body, settings.DEFAULT_FROM_EMAIL, [recipient])

    if settings.FAHRRADPARKEN_REPLY_TO is not None:
        email.reply_to = [settings.FAHRRADPARKEN_REPLY_TO]

    email.send(fail_silently=True)
