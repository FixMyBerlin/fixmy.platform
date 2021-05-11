from django.db import models
from django.utils.translation import gettext_lazy as _
from fixmyapp.models.base_model import BaseModel
import numpy


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

    project = models.PositiveSmallIntegerField(_('project'))
    experiment = models.CharField(
        _('experiment'), choices=EXPERIMENT_CHOICES, max_length=2
    )
    perspective = models.CharField(
        _('perspective'), choices=PERSPECTIVE_CHOICES, max_length=1
    )
    number = models.PositiveIntegerField(_('number'))
    weight = models.PositiveSmallIntegerField(_('weight'))
    image = models.ImageField(_('image'), upload_to='KatasterKI/scenes')

    class Meta:
        unique_together = ('project', 'experiment', 'perspective', 'number')
        verbose_name = _('scene')
        verbose_name_plural = _('scenes')

    def __str__(self):
        return '{:02}_{}_{}_{}'.format(
            self.project, self.experiment, self.perspective, self.number
        )

    @classmethod
    def find_by_scene_id(cls, scene_id):
        parts = scene_id.split('_')
        return cls.objects.get(
            project=parts[0], experiment=parts[1], perspective=parts[2], number=parts[3]
        )

    @classmethod
    def random_group(cls, perspective, project, size):
        scenes = cls.objects.filter(perspective=perspective, project=project)
        d = sum(s.weight for s in scenes)
        p = [s.weight / d for s in scenes]
        return numpy.random.choice(scenes, size, replace=False, p=p)


class Session(BaseModel):
    id = models.UUIDField(_('id'), primary_key=True)
    profile = models.JSONField(_('profile'))
    project = models.PositiveSmallIntegerField(_('project'))

    class Meta:
        verbose_name = _('session')
        verbose_name_plural = _('sessions')


class Rating(BaseModel):
    duration = models.PositiveIntegerField(_('duration'), null=True)
    rating = models.PositiveSmallIntegerField(_('rating'), null=True)
    scene = models.ForeignKey(Scene, on_delete=models.SET_NULL, null=True)
    session = models.ForeignKey(
        Session, related_name='ratings', on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = _('rating')
        verbose_name_plural = _('ratings')
