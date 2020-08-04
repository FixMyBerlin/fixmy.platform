from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _

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
