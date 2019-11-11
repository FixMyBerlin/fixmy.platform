from django.db import models
from django.utils.translation import gettext_lazy as _
from fixmyapp.models import BaseModel


class Scene(BaseModel):
    EXPERIMENT_CP = 'CP'
    EXPERIMENT_MS = 'MS'
    EXPERIMENT_SI = 'SI'
    EXPERIMENT_CHOICES = (
        (EXPERIMENT_CP, _('cycle path')),
        (EXPERIMENT_MS, _('main street')),
        (EXPERIMENT_SI, _('side street')),
    )

    PERSPECTIVE_A = 'A'
    PERSPECTIVE_C = 'C'
    PERSPECTIVE_P = 'P'
    PERSPECTIVE_CHOICES = (
        (PERSPECTIVE_A, _('car')),
        (PERSPECTIVE_C, _('bicycle')),
        (PERSPECTIVE_P, _('pedestrian')),
    )

    experiment = models.CharField(
        _('experiment'), choices=EXPERIMENT_CHOICES, max_length=2
    )
    image = models.ImageField(_('image'), upload_to='KatasterKI/scenes')
    number = models.PositiveIntegerField(_('number'))
    perspective = models.CharField(
        _('perspective'), choices=PERSPECTIVE_CHOICES, max_length=1
    )
    project = models.PositiveSmallIntegerField(_('project'))
    weight = models.PositiveSmallIntegerField(_('weight'))

    class Meta:
        verbose_name = _('scene')
        verbose_name_plural = _('scenes')

    def __str__(self):
        return '{:02}_{}_{}_{}'.format(
            self.project, self.experiment, self.perspective, self.number)
