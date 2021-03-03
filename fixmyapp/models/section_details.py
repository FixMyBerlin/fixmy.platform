from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _
import decimal

from .base_model import BaseModel
from .photo import Photo
from .section import Section


class SectionDetails(BaseModel):
    RIGHT = 0
    LEFT = 1
    SIDE_CHOICES = ((RIGHT, _('right')), (LEFT, _('left')))
    NORTH = 'N'
    EAST = 'E'
    SOUTH = 'S'
    WEST = 'W'
    ORIENTATION_CHOICES = (
        (NORTH, _('north')),
        (EAST, _('east')),
        (SOUTH, _('south')),
        (WEST, _('west')),
    )
    AVG_WIDTH_CROSSINGS = 6
    CI_RATIO_MIN = 0.65

    section = models.ForeignKey(
        Section, related_name='details', on_delete=models.CASCADE
    )
    side = models.PositiveSmallIntegerField(_('side'), choices=SIDE_CHOICES)
    speed_limit = models.PositiveSmallIntegerField(_('speed limit'))
    daily_traffic = models.DecimalField(
        _('daily traffic'), max_digits=8, decimal_places=2
    )
    daily_traffic_heavy = models.DecimalField(
        _('daily traffic heavy'), max_digits=8, decimal_places=2
    )
    daily_traffic_cargo = models.DecimalField(
        _('daily traffic cargo'), max_digits=8, decimal_places=2
    )
    daily_traffic_bus = models.DecimalField(
        _('daily traffic bus'), max_digits=8, decimal_places=2
    )
    length = models.DecimalField(_('length'), max_digits=8, decimal_places=2)
    crossings = models.PositiveSmallIntegerField(_('crossings'))
    orientation = models.CharField(
        _('orientation'), max_length=1, choices=ORIENTATION_CHOICES
    )
    rva1 = models.DecimalField(max_digits=16, decimal_places=12)
    rva2 = models.DecimalField(max_digits=16, decimal_places=12)
    rva3 = models.DecimalField(max_digits=16, decimal_places=12)
    rva4 = models.DecimalField(max_digits=16, decimal_places=12)
    rva5 = models.DecimalField(max_digits=16, decimal_places=12)
    rva6 = models.DecimalField(max_digits=16, decimal_places=12)
    rva7 = models.DecimalField(max_digits=16, decimal_places=12)
    rva8 = models.DecimalField(max_digits=16, decimal_places=12)
    rva9 = models.DecimalField(max_digits=16, decimal_places=12)
    rva10 = models.DecimalField(max_digits=16, decimal_places=12)
    rva11 = models.DecimalField(max_digits=16, decimal_places=12)
    rva12 = models.DecimalField(max_digits=16, decimal_places=12)
    rva13 = models.DecimalField(max_digits=16, decimal_places=12)
    photos = GenericRelation(Photo)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['section', 'side'], name='unique_section_details_dataset'
            )
        ]
        verbose_name = _('Section details')
        verbose_name_plural = _('Section details')

    def happy_bike_index(self):
        return self.velocity_index() + self.safety_index()

    def velocity_index(self):
        weighted_sum = sum(
            [
                self.rva3 * 2,
                self.rva4 * 1,
                self.rva7 * 2,
                self.rva8 * 3,
                self.rva9 * 3,
                self.rva10 * 3,
                self.rva11 * 2,
                self.rva12 * 3,
                self.rva13 * 2,
            ]
        )

        if self.cycling_infrastructure_sum() > 0:
            ci_factor = weighted_sum / (self.cycling_infrastructure_sum() * 3)
        else:
            ci_factor = decimal.Decimal(weighted_sum / 3)

        if self.cycling_infrastructure_ratio() < self.CI_RATIO_MIN:
            return self.cycling_infrastructure_ratio() * ci_factor + (
                1 - self.cycling_infrastructure_ratio()
            )
        else:
            return ci_factor

    def safety_index(self):
        offset = decimal.Decimal(3)
        ci_safety = self.cycling_infrastructure_safety()

        if ci_safety <= self.road_type():
            return (offset + ci_safety - self.road_type()) * decimal.Decimal('2.25')
        else:
            return (offset + (ci_safety - self.road_type()) / 3) * decimal.Decimal(
                '2.25'
            )

    def length_without_crossings(self):
        """Returns length of section without crossings

        We do not count crossings as cycling infrastructure.
        """
        return self.length - self.AVG_WIDTH_CROSSINGS * self.crossings

    def cycling_infrastructure_sum(self):
        """Returns the length of all cycling infrastructure

        Some fields are ignored because we do not count them as cycling
        infrastructure.
        """
        return sum(
            [
                self.rva3,
                self.rva4,
                self.rva5,
                self.rva6,
                self.rva7,
                self.rva8,
                self.rva9,
                self.rva10,
                self.rva11,
                self.rva12,
                self.rva13,
            ]
        )

    def bike_path_sum(self):
        """Returns the length of all bike paths

        Bike paths are paths with their own right of way dedicated to cycling,
        though in many cases shared with pedestrians and other non-motorized
        traffic.
        """
        return sum([self.rva3, self.rva4, self.rva10])

    def shared_use_path_sum(self):
        """Returns the length of all shared use paths

        A shared use path supports multiple modes, such as walking, bicycling,
        inline skating and people in wheelchairs.
        """
        return sum([self.rva5, self.rva6])

    def bike_lane_sum(self):
        """Returns the length of all bike lanes

        Bike lanes or cycle lanes, are on-road lanes marked with paint
        dedicated to cycling and typically excluding all motorized traffic.
        """
        return self.rva7

    def protected_bike_lane_sum(self):
        """Returns the length of all protected bike lanes

        A cycle track, also called separated bike lane or protected bike lane,
        is a physically marked and separated lane dedicated for cycling that is
        on or directly adjacent to the roadway but typically excludes all
        motorized traffic with some sort of vertical barrier.
        """
        return sum([self.rva8, self.rva9])

    def advisory_bike_lane_sum(self):
        """Returns the length of all advisory bike lanes

        An advisory bike lane is a roadway striping configuration which
        provides for two-way motor vehicle and bicycle traffic using a central
        vehicular travel lane and “advisory” bike lanes on either side.
        """
        return sum([self.rva11, self.rva12, self.rva13])

    def cycling_infrastructure_ratio(self):
        rv = decimal.Decimal('0.00')
        try:
            rv = self.cycling_infrastructure_sum() / self.length_without_crossings()
        except decimal.DivisionByZero:
            pass
        return rv

    def bike_path_ratio(self):
        return self._ci_category_ratio(self.bike_path_sum())

    def shared_use_path_ratio(self):
        return self._ci_category_ratio(self.shared_use_path_sum())

    def bike_lane_ratio(self):
        return self._ci_category_ratio(self.bike_lane_sum())

    def protected_bike_lane_ratio(self):
        return self._ci_category_ratio(self.protected_bike_lane_sum())

    def advisory_bike_lane_ratio(self):
        return self._ci_category_ratio(self.advisory_bike_lane_sum())

    def road_type(self):
        """Returns a number categorizing traffic intensity"""

        if self.speed_limit <= 20:
            l = (11000, 18000, 20000)
        elif self.speed_limit <= 30:
            l = (8000, 18000, 20000)
        elif self.speed_limit <= 40:
            l = (6000, 16000, 19000)
        elif self.speed_limit <= 50:
            l = (4000, 10000, 18000)
        elif self.speed_limit <= 60:
            l = (2000, 5000, 7000)
        else:
            l = (2000, 3000, 6000)

        if self.daily_traffic <= l[0]:
            return self.daily_traffic / l[0]
        elif self.daily_traffic <= l[1]:
            return 1 + (self.daily_traffic - l[0]) / (l[1] - l[0])
        elif self.daily_traffic <= l[2]:
            return 2 + (self.daily_traffic - l[1]) / (l[2] - l[1])
        else:
            return 3

    def cycling_infrastructure_safety(self):
        weighted_sum = sum(
            [
                self.rva3 * 3,
                self.rva4 * 3,
                self.rva5 * 3,
                self.rva6 * 3,
                self.rva7 * 2,
                self.rva8 * 3,
                self.rva9 * 3,
                self.rva10 * 3,
                self.rva11 * 1,
                self.rva12 * 1,
                self.rva13 * 1,
            ]
        )
        if self.cycling_infrastructure_ratio() < self.CI_RATIO_MIN:
            safety = 0
        else:
            safety = weighted_sum / self.cycling_infrastructure_sum()
        return safety

    def _ci_category_ratio(self, category_sum):
        if self.cycling_infrastructure_ratio() < 0.1:
            ratio = 0.0
        else:
            ratio = category_sum / self.length_without_crossings()
        return ratio

    def __str__(self):
        return '{} {}'.format(self.section, self.SIDE_CHOICES[self.side][1])
