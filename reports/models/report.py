from django.conf import settings
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

    REPORT_STATUSES = (
        STATUS_REPORT_ACCEPTED,
        STATUS_REPORT_INACTIVE,
        STATUS_REPORT_NEW,
        STATUS_REPORT_REJECTED,
        STATUS_REPORT_VERIFICATION,
    )
    PLANNING_STATUSES = (
        STATUS_PLANNING,
        STATUS_TENDER,
        STATUS_INVALID,
        STATUS_EXECUTION,
        STATUS_DONE,
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
        'self',
        related_name='plannings',
        verbose_name=_('origin reports'),
        blank=True,
        symmetrical=False,
    )

    class Meta:
        verbose_name = _('report')
        verbose_name_plural = _('reports')

    def __init__(self, *args, **kwargs):
        super(Report, self).__init__(*args, **kwargs)
        # prev status is saved to detect status change in self.save()
        self.__prev_status = self.status

    def __str__(self):
        kind = _('report') if self.is_report else _('planning')
        return f"{kind} {self.id} ({_(self.status)})"

    def enqueue_notifications(self):
        """Prepare notifications to user by creating StatusNotice objects

        StatusNotice objects can be processed by calling the management command
        `sendnotifications`.

        !!! No notices are created when updating reports with the queryset
        method `update`. Always update report status through `Report.save` unless
        you don't want to enqueue notices!"""

        from .status_notice import StatusNotice

        notified_users = set()

        def notify_user(user):
            if user is not None and user not in notified_users:
                notified_users.add(user)
                StatusNotice.create(status=self.status, user=user, report=self)

        # Remove all unsent notifications about this report to prevent
        # duplicate notifications
        StatusNotice.objects.filter(report=self, sent=False).delete()

        if self.user is not None:
            notify_user(self.user)

        for like in self.likes.all():
            notify_user(like.user)

        for report in self.origin.all():
            notify_user(report.user)

    @property
    def is_planning(self):
        return self.status in self.PLANNING_STATUSES

    @property
    def is_report(self):
        return self.status in self.REPORT_STATUSES

    def save(self, *args, **kwargs):
        super(Report, self).save(*args, **kwargs)

        if self.status != self.__prev_status:
            self.enqueue_notifications()

    @property
    def frontend_url(self):
        return f"{settings.FRONTEND_URL}/redirect-to/reports/{self.id}"
