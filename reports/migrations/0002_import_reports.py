from django.db import migrations
from django.forms import model_to_dict
from django.contrib.contenttypes.models import ContentType
from sys import stdout


def import_reports(apps, schema_editor):
    """Import reports from fixmyapp.reports"""

    Report = apps.get_model('reports', 'BikeStands')
    try:
        from fixmyapp.models import Report as ReportDangerousDirect

        ReportLegacy = apps.get_model('fixmyapp', 'BikeStands')
        stdout.write("Success loading fixmyapp.report model. ")
    except Exception:
        stdout.write("Not migrating reports data as fixmyapp.report does not exist")
        return

    # ct is the content type of the GenericRelation objects linking reports
    # to likes and photos
    ct = ContentType.objects.get_for_model(Report, for_concrete_model=False)

    stdout.write(f"Migrating {ReportLegacy.objects.count()} reports...")

    for source in ReportLegacy.objects.all():
        data = model_to_dict(source, exclude=['user', 'likes', 'photo', 'report_ptr'])
        target = Report(**data)
        target.number = source.number
        target.fee_acceptable = source.fee_acceptable
        target.user = source.user
        target.save()

        target.created_date = source.created_date
        target.modified_date = source.modified_date
        # override auto_now and auto_now_add
        target.save(update_fields=['created_date', 'modified_date'])

        # As generic relation fields are not accessible in the fake models
        # obtained from apps.get_model, this tries to retrieve a list of likes
        # and photos through the current
        report_direct = ReportDangerousDirect.objects.get(pk=source.report_ptr.id)

        for like in report_direct.likes.all():
            # Set id to None to `Insert` instead of `Update`
            like.id = None
            like.content_object = target
            like.content_type = ct
            like.save()

        for photo in report_direct.photo.all():
            photo.id = None
            photo.content_object = target
            photo.content_type = ct
            photo.save()


def un_import_reports(apps, schema_editor):
    Like = apps.get_model('fixmyapp', 'Like')
    Like.objects.filter(content_type__app_label='reports').delete()

    Photo = apps.get_model('fixmyapp', 'Photo')
    Photo.objects.filter(content_type__app_label='reports').delete()


class Migration(migrations.Migration):

    dependencies = [('reports', '0001_initial')]

    operations = [migrations.RunPython(import_reports, un_import_reports)]
