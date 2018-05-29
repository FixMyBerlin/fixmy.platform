from fixmyapp.models import Edge, PlanningSection
import csv


def import_planning_sections(file_like):
    reader = csv.DictReader(file_like)
    for row in reader:
        obj, created = PlanningSection.objects.get_or_create(
            pk=row['MetaID']
        )
        obj.name = row['Straßen Name']
        obj.edges.add(Edge.objects.get(pk=row['ElemNr']))
        obj.geom_hash = obj.compute_geom_hash()
        obj.save()
