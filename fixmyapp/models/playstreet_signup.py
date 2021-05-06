import json

from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _
from django.template.loader import render_to_string
from django.conf import settings
from django.core import mail

from .base_model import BaseModel


class PlaystreetSignup(BaseModel):
    campaign = models.CharField(_('campaign'), max_length=64)
    street = models.CharField(_('play_street'), max_length=128)
    first_name = models.TextField(_('first_name'))
    last_name = models.TextField(_('last_name'))
    email = models.CharField(_('email'), max_length=255)
    tos_accepted = models.BooleanField(_('tos_accepted'), default=False)
    captain = models.BooleanField(_('captain'), default=False)
    message = models.TextField(_('message'), blank=True)

    class Meta:
        verbose_name = _('playstreet_signup')
        verbose_name_plural = _('playstreet_signups')
        ordering = ['campaign', 'street']

    @classmethod
    def send_notification(cls, serializer):
        """Send notification about this signup to a configured email address."""

        context = serializer.data
        context['captain_text'] = "Ja" if serializer.data.get('captain') else "Nein"
        context['message_text'] = serializer.data.get('message')

        subject = 'Neue Unterstützung für eine Spielstraße'
        body = render_to_string('playstreets/notice_registered.txt', context=context)
        m = mail.send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [settings.PLAYSTREET_RECIPIENT],
            fail_silently=True,
        )