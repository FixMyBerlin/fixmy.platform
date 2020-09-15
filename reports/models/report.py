from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _

from fixmyapp.models import BaseModel, Like, Photo


class Report(BaseModel):
    STATUS_REPORT_NEW = 'report_new'
    STATUS_REPORT_VERIFICATION = 'report_verification'
    STATUS_REPORT_ACCEPTED = 'report_accepted'
    STATUS_REPORT_REJECTED = 'report_rejected'
    STATUS_REPORT_INACTIVE = 'report_inactive'
    STATUS_PLANNING = 'planning'
    STATUS_TENDER = 'tender'
    STATUS_INVALID = 'invalid'
    STATUS_EXECUTION = 'execution'
    STATUS_DONE = 'done'

    STATUS_CHOICES = (
        (STATUS_REPORT_NEW, _('new')),
        (STATUS_REPORT_VERIFICATION, _('verification')),
        (STATUS_REPORT_ACCEPTED, _('accepted')),
        (STATUS_REPORT_REJECTED, _('rejected')),
        (STATUS_REPORT_INACTIVE, _('inactive')),
        (STATUS_PLANNING, _('planning')),
        (STATUS_TENDER, _('tender')),
        (STATUS_INVALID, _('invalid')),
        (STATUS_EXECUTION, _('execution')),
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
        default=STATUS_REPORT_NEW,
    )
    status_reason = models.TextField(_('reason for status'), blank=True, null=True)
    user = models.ForeignKey(
        get_user_model(), blank=True, null=True, on_delete=models.SET_NULL
    )
    origin = models.ManyToManyField(
        'self', related_name='plannings', blank=True, symmetrical=False
    )

    class Meta:
        verbose_name = _('report')
        verbose_name_plural = _('reports')

    def __str__(self):
        return f"Report {self.id} ({_(self.status)}"
