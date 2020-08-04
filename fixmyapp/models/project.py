from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _
from markdownx.models import MarkdownxField

from .base_model import BaseModel
from .like import Like
from .photo import Photo
from .question import Question


class Project(BaseModel):
    CATEGORY_NEW_INFRASTRUCTURE = 'new cycling infrastructure'
    CATEGORY_RENOVATION = 'renovation of cycling infrastructure'
    CATEGORY_BIKE_STREET = 'bike street'
    CATEGORY_MODIFICATION_OF_JUNCTION = 'modification of junction'
    CATEGORY_BIKE_PARKING = 'bike parking'
    CATEGORY_CROSSING_AID = 'crossing aid'
    CATEGORY_MODIFICATION_OF_CROSS_SECTION = 'modification of cross section'
    CATEGORY_NEW_STREET = 'new street'
    CATEGORY_SHARED_SPACE = 'shared space'
    CATEGORY_MISCELLANEOUS = 'miscellaneous'

    CATEGORY_CHOICES = (
        (CATEGORY_NEW_INFRASTRUCTURE, _('new cycling infrastructure')),
        (CATEGORY_RENOVATION, _('renovation of cycling infrastructure')),
        (CATEGORY_BIKE_STREET, _('bike street')),
        (CATEGORY_MODIFICATION_OF_JUNCTION, _('modification of junction')),
        (CATEGORY_BIKE_PARKING, _('bike parking')),
        (CATEGORY_CROSSING_AID, _('crossing aid')),
        (CATEGORY_MODIFICATION_OF_CROSS_SECTION, _('modification of cross section')),
        (CATEGORY_NEW_STREET, _('new street')),
        (CATEGORY_SHARED_SPACE, _('shared space')),
        (CATEGORY_MISCELLANEOUS, _('miscellaneous')),
    )

    PHASE_DRAFT = 'draft'
    PHASE_PLANNING = 'planning'
    PHASE_REVIEW = 'review'
    PHASE_INACTIVE = 'inactive'
    PHASE_EXECUTION = 'execution'
    PHASE_READY = 'ready'
    PHASE_MISCELLANEOUS = 'miscellaneous'

    PHASE_CHOICES = (
        (PHASE_DRAFT, _('draft')),
        (PHASE_PLANNING, _('planning')),
        (PHASE_REVIEW, _('review')),
        (PHASE_INACTIVE, _('inactive')),
        (PHASE_EXECUTION, _('execution')),
        (PHASE_READY, _('ready')),
        (PHASE_MISCELLANEOUS, _('miscellaneous')),
    )

    STATUS_UNKNOWN = 'unknown'
    STATUS_IDEA = 'idea'
    STATUS_PRELIMINARY_PLANNING = 'preliminary planning'
    STATUS_BLUEPRINT_PLANNING = 'blueprint planning'
    STATUS_APPROVAL_PLANNING = 'approval planning'
    STATUS_EXAMINATION = 'examination'
    STATUS_EXECUTION_PLANNING = 'execution planning'
    STATUS_PREPARATION_OF_AWARDING = 'preparation of awarding'
    STATUS_AWARDING = 'awarding'
    STATUS_APPLICATION_FOR_CONSTRUCTION_SITE = 'application for construction site'
    STATUS_EXECUTION_OF_CONSTRUCTION_WORK = 'execution of construction work'
    STATUS_READY = 'ready'
    STATUS_REVIEW = 'review'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = (
        (STATUS_UNKNOWN, _('unknown')),
        (STATUS_IDEA, _('idea')),
        (STATUS_PRELIMINARY_PLANNING, _('preliminary planning')),
        (STATUS_BLUEPRINT_PLANNING, _('blueprint planning')),
        (STATUS_APPROVAL_PLANNING, _('approval planning')),
        (STATUS_EXAMINATION, _('examination')),
        (STATUS_EXECUTION_PLANNING, _('execution planning')),
        (STATUS_PREPARATION_OF_AWARDING, _('preparation of awarding')),
        (STATUS_AWARDING, _('awarding')),
        (
            STATUS_APPLICATION_FOR_CONSTRUCTION_SITE,
            _('application for construction site'),
        ),
        (STATUS_EXECUTION_OF_CONSTRUCTION_WORK, _('execution of construction work')),
        (STATUS_READY, _('ready')),
        (STATUS_REVIEW, _('review')),
        (STATUS_CANCELLED, _('cancelled')),
    )

    RIGHT = 0
    LEFT = 1
    BOTH = 2
    SIDE_CHOICES = ((RIGHT, _('right')), (LEFT, _('left')), (BOTH, _('both')))

    TRANSFORM_EPSG_3035 = 3035

    project_key = models.CharField(_('project key'), max_length=100, unique=True)
    published = models.BooleanField(_('published'), default=True)
    title = models.CharField(_('title'), max_length=256)
    side = models.PositiveSmallIntegerField(_('side'), choices=SIDE_CHOICES)
    responsible = models.CharField(_('responsible'), max_length=256)
    description = MarkdownxField(_('description'))
    short_description = models.CharField(
        _('short description'), blank=True, null=True, max_length=200
    )
    geometry = models.GeometryField(_('geometry'), blank=True, null=True)
    category = models.CharField(
        _('category'), blank=True, null=True, max_length=40, choices=CATEGORY_CHOICES
    )
    street_name = models.CharField(_('street name'), max_length=100)
    borough = models.CharField(_('borough'), blank=True, null=True, max_length=255)
    costs = models.PositiveIntegerField(_('costs'), blank=True, null=True)
    draft_submitted = models.CharField(
        _('draft submitted'), blank=True, null=True, max_length=100
    )
    construction_started = models.CharField(
        _('construction started'), blank=True, null=True, max_length=100
    )
    construction_completed = models.CharField(
        _('construction completed'),
        blank=True,
        null=True,
        default=_('unknown'),
        max_length=100,
    )
    construction_completed_date = models.DateField(
        _('construction completed date'), blank=True, null=True
    )
    alert_date = models.DateField(_('alert date'), blank=True, null=True)
    phase = models.CharField(
        _('phase'), blank=True, null=True, max_length=30, choices=PHASE_CHOICES
    )
    status = models.CharField(
        _('status'), blank=True, null=True, max_length=40, choices=STATUS_CHOICES
    )
    external_url = models.URLField(_('external URL'), blank=True, null=True)
    cross_section = models.ImageField(
        _('cross section'), upload_to='photos', blank=True, null=True
    )
    faq = models.ManyToManyField(Question, verbose_name=_('faq'), blank=True)
    photos = GenericRelation(Photo)
    likes = GenericRelation(Like)

    class Meta:
        verbose_name = _('project')
        verbose_name_plural = _('projects')

    def center(self):
        if self.geometry:
            return self.geometry.point_on_surface

    def length(self):
        if self.geometry:
            return self.geometry.transform(self.TRANSFORM_EPSG_3035, clone=True).length

    def __str__(self):
        return self.project_key
