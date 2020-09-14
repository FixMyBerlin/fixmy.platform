# Generated by Django 3.0.7 on 2020-09-14 11:52

from sys import stdout
from django.db import migrations


def fix_reports(apps, _):
    """Re-attach likes and photos to reports that were not migrated in 0002"""
    from fixmyapp.models import BikeStands as ReportLegacy

    Report = apps.get_model('reports', 'report')
    Like = apps.get_model('fixmyapp', 'like')
    Photo = apps.get_model('fixmyapp', 'photo')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    like_count = 0
    photo_count = 0

    for source in ReportLegacy.objects.all():
        target = Report.objects.get(pk=source.id)
        if target is None:
            raise KeyError(
                f'Target report with id {source.id} not found. It should have been created by the previous reports migration 0002.'
            )

        likes = Like.objects.filter(
            object_id=source.id,
            content_type__model='report',
            content_type__app_label='fixmyapp',
        )
        for like_source in likes:
            Like.objects.create(
                content_type=ContentType.objects.get(
                    app_label='reports', model='report'
                ),
                object_id=target.id,
                user=like_source.user,
            )
            like_count += 1

        photos = Photo.objects.filter(
            object_id=source.id,
            content_type__model='report',
            content_type__app_label='fixmyapp',
        )
        for photo_source in photos:
            Photo.objects.create(
                content_type=ContentType.objects.get(
                    app_label='reports', model='report'
                ),
                object_id=target.id,
                copyright=photo_source.copyright,
                src=photo_source.src,
            )
            photo_count += 1
    stdout.write(f"Created {like_count} likes and {photo_count} photos. ")


def un_fix_reports(apps, _):
    # Objects created by this migration are deleted through cascade, so nothing
    # to do here
    pass


class Migration(migrations.Migration):

    dependencies = [('reports', '0003_auto_20200910_1224')]

    operations = [migrations.RunPython(fix_reports, un_fix_reports)]

