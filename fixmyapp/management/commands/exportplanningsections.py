from django.contrib.gis.db.models import Union
from django.core.management.base import BaseCommand
from django.urls import reverse
from fixmyapp.models import Planning, PlanningSection
import argparse
import copy
import json
import sys


class Command(BaseCommand):
    help = 'Exports planning sections as GeoJSON'

    def add_arguments(self, parser):
        parser.add_argument(
            'file',
            type=argparse.FileType('w'),
            default=sys.stdout,
            help='A file'
        )
        parser.add_argument(
            '--has-planning',
            action='store_true',
            help='only include planning sections with plannings'
        )
        parser.add_argument(
            '--indent',
            type=int,
            default=None,
            help='indentation level for pretty printing'
        )

    def handle(self, *args, **options):
        result = {
            'type': 'FeatureCollection',
            'features': []
        }

        if options['has_planning']:
            qs = PlanningSection.objects.filter(plannings__isnull=False)
        else:
            qs = PlanningSection.objects.all()

        for p in qs:
            geometry = p.geometry()
            feature = {
                'type': 'Feature',
                'geometry': json.loads(geometry.json),
                'properties': {
                    'id': p.pk,
                    'name': p.name,
                    'velocity': float(round(p.velocity_index(), 3)),
                    'safety': float(round(p.safety_index(), 3))
                }
            }

            for detail in p.details.all():
                prefix = 'side{}_'.format(detail.side)
                feature['properties'][prefix + 'orientation'] = detail.orientation
                feature['properties'][prefix + 'velocity'] = float(round(detail.velocity_index(), 3))
                feature['properties'][prefix + 'safety'] = float(round(detail.safety_index(), 3))

            if p.has_plannings():
                feature['properties'].update(
                    self.properties_from_plannings(list(p.plannings.all())))

            result['features'].append(feature)

            center = {
                'type': 'Feature',
                'geometry': json.loads(geometry.point_on_surface.json),
                'properties': {
                    'id': p.pk
                }
            }

            result['features'].append(center)

        json.dump(result, options['file'], indent=options['indent'])


    def properties_from_plannings(self, plannings):
        properties = {}

        if len(plannings) == 1 and plannings[0].side == Planning.BOTH:
            plannings.append(copy.copy(plannings[0]))
            plannings[0].side = Planning.RIGHT
            plannings[1].side = Planning.LEFT

        for planning in plannings:
            prefix = 'side{}_'.format(planning.side)
            planning_url = reverse('planning-detail', args=[planning.id])
            properties[prefix + 'planning_id'] = planning.id
            properties[prefix + 'planning_url'] = planning_url
            properties[prefix + 'planning_title'] = planning.title
            properties[prefix + 'planning_phase'] = planning.phase

        if len(plannings) == 2:
            if plannings[0].phase is not None and plannings[1].phase is not None:
                properties['planning_phase'] = Planning.PHASE_CHOICES[max(
                    Planning.PHASE_CHOICES.index(
                        (plannings[0].phase, plannings[0].phase)),
                    Planning.PHASE_CHOICES.index(
                        (plannings[1].phase, plannings[1].phase))
                )][1]
            elif plannings[0].phase is not None:
                properties['planning_phase'] = plannings[0].phase
            else:
                properties['planning_phase'] = plannings[1].phase
        else:
            properties['planning_phase'] = plannings[0].phase

        return properties
