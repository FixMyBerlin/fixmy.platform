from django.core.management.base import BaseCommand
from fixmyapp.models import Like, Photo, Planning, Project


class Command(BaseCommand):
    help = 'Copy planning instances to projects'

    def handle(self, *args, **options):
        for planning in Planning.objects.all():
            project = Project(
                id=planning.id,
                published=planning.published,
                title=planning.title,
                side=planning.side,
                responsible=planning.responsible,
                description=planning.description,
                short_description=planning.short_description,
                category=planning.category,
                project_key=planning.project_key,
                street_name=planning.planning_sections.first().name,
                borough=planning.planning_sections.first().borough(),
                costs=planning.costs,
                draft_submitted=planning.draft_submitted,
                construction_started=planning.construction_started,
                construction_completed=planning.construction_completed,
                phase=planning.phase,
                status=planning.status,
                external_url=planning.external_url,
                cross_section=planning.cross_section_photo,
                created_date=planning.created_date,
                modified_date=planning.modified_date
            )
            project.save()
            project.faq.set(planning.faq.all())

            # Generic relations - like, photo - need to be iterated over 
            # to copy them to a new object
            
            for photo in planning.photos.all():
                project.photos.add(
                    Photo(
                        src=photo.src,
                        copyright=photo.copyright,
                        created_date=photo.created_date,
                        modified_date=photo.modified_date),
                    bulk=False)

            for like in planning.likes.all():
                project.likes.add(
                    Like(
                        user=like.user,
                        created_date=like.created_date,
                        modified_date=like.modified_date),
                    bulk=False)
