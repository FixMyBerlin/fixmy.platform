from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _

from .base_model import BaseModel
from .like import Like
from .photo import Photo


class Report(BaseModel):
    STATUS_NEW = 'new'
    STATUS_VERIFICATION = 'verification'
    STATUS_ACCEPTED = 'accepted'
    STATUS_REJECTED = 'rejected'
    STATUS_DONE = 'done'

    STATUS_CHOICES = (
        (STATUS_NEW, _('new')),
        (STATUS_VERIFICATION, _('verification')),
        (STATUS_ACCEPTED, _('accepted')),
        (STATUS_REJECTED, _('rejected')),
        (STATUS_DONE, _('done')),
    )

    SUBJECT_BIKE_STANDS = 'BIKE_STANDS'
    SUBJECT_CHOICES = ((SUBJECT_BIKE_STANDS, _('bike stands')),)

    address = models.TextField(_('address'), blank=True, null=True)
    geometry = models.PointField(_('geometry'), srid=4326)
    subject = models.CharField(_('subject'), max_length=100, choices=SUBJECT_CHOICES)
    description = models.CharField(
        _('description'), blank=True, null=True, max_length=1000
    )
    likes = GenericRelation(Like)
    photo = GenericRelation(Photo)
    published = models.BooleanField(_('published'), default=True)
    status = models.CharField(
        _('status'),
        blank=True,
        null=True,
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_NEW,
    )
    status_reason = models.TextField(_('reason for status'), blank=True, null=True)
    user = models.ForeignKey(
        get_user_model(), blank=True, null=True, on_delete=models.SET_NULL
    )

    class Meta:
        verbose_name = _('report')
        verbose_name_plural = _('reports')
