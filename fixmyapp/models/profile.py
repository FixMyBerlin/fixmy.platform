from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _
import uuid

from .base_model import BaseModel


class Profile(BaseModel):
    MALE = 'm'
    FEMALE = 'f'
    OTHER = 'o'
    SEX_CHOICES = ((MALE, _('male')), (FEMALE, _('female')), (OTHER, _('other')))
    RACING_CYCLE = 'racing_cycle'
    CITY_BIKE = 'city_bike'
    MOUNTAIN_BIKE = 'mountain_bike'
    E_BIKE = 'e_bike'
    CARGO_BIKE = 'cargo_bike'
    E_CARGO_BIKE = 'e_cargo_bike'
    CATEGORY_OF_BIKE_CHOICES = (
        (RACING_CYCLE, _('racing cycle')),
        (CITY_BIKE, _('city bike')),
        (MOUNTAIN_BIKE, _('mountain bike')),
        (E_BIKE, _('e-bike')),
        (CARGO_BIKE, _('cargo bike')),
        (E_CARGO_BIKE, _('e-cargo-bike')),
    )
    NEVER = 0
    ONCE_PER_MONTH = 1
    ONCE_PER_WEEK = 2
    ONCE_PER_DAY = 3
    USAGE_CHOICES = (
        (NEVER, _('never')),
        (ONCE_PER_DAY, _('once per day')),
        (ONCE_PER_WEEK, _('once per week')),
        (ONCE_PER_MONTH, _('once per month')),
    )
    age = models.PositiveSmallIntegerField(_('age'), blank=True, null=True)
    category_of_bike = models.CharField(
        _('category of bike'),
        blank=True,
        null=True,
        max_length=20,
        choices=CATEGORY_OF_BIKE_CHOICES,
    )
    has_trailer = models.BooleanField(_('has trailer'), blank=True, null=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    postal_code = models.CharField(
        _('postal code'), blank=True, null=True, max_length=5
    )
    sex = models.CharField(
        _('sex'), blank=True, null=True, max_length=1, choices=SEX_CHOICES
    )
    speed = models.PositiveSmallIntegerField(_('speed'), blank=True, null=True)
    security = models.PositiveSmallIntegerField(_('security'), blank=True, null=True)
    usage = models.PositiveSmallIntegerField(
        _('usage'), blank=True, null=True, choices=USAGE_CHOICES
    )

    class Meta:
        verbose_name = _('profile')
        verbose_name_plural = _('profiles')
