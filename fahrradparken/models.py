import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _

from fixmyapp.models.base_model import BaseModel


class Signup(BaseModel):
    # personal details
    affiliation = models.CharField(_('affiliation'), max_length=255)
    first_name = models.CharField(_('first name'), max_length=255)
    last_name = models.CharField(_('last name'), max_length=255)
    role = models.CharField(_('role'), max_length=255)
    email = models.CharField(_('email'), max_length=255)
    phone = models.CharField(
        _('telephone number'), max_length=32, null=True, blank=True
    )

    # regarding bicycle parking at their train station
    station_name = models.CharField(_('name of station'), max_length=255)
    message = models.TextField(_('message'), blank=True, null=True)

    newsletter = models.BooleanField(_('requests newsletter'), default=True)


class EventSignup(Signup):
    event_id = models.IntegerField(_('event'))
    event_title = models.CharField(_('event title'), max_length=255)
    event_date = models.CharField(_('event date'), max_length=255)
    event_time = models.CharField(_('event time'), max_length=255)
