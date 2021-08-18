# Generated by Django 3.1.6 on 2021-05-19 14:08

from django.db import migrations, models
import permits.models


class Migration(migrations.Migration):

    dependencies = [
        ('permits', '0003_event_address_field'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventpermit',
            name='agreement',
            field=models.FileField(
                max_length=255,
                upload_to=permits.models.EventPermit.agreement_upload_to,
                verbose_name='event agreement',
            ),
        ),
        migrations.AlterField(
            model_name='eventpermit',
            name='insurance',
            field=models.FileField(
                max_length=255,
                upload_to=permits.models.EventPermit.insurance_upload_to,
                verbose_name='proof of insurance',
            ),
        ),
        migrations.AlterField(
            model_name='eventpermit',
            name='public_benefit',
            field=models.FileField(
                blank=True,
                max_length=255,
                null=True,
                upload_to=permits.models.EventPermit.public_benefit_upload_to,
                verbose_name='proof of public benefit',
            ),
        ),
        migrations.AlterField(
            model_name='eventpermit',
            name='setup_sketch',
            field=models.FileField(
                blank=True,
                max_length=255,
                null=True,
                upload_to=permits.models.EventPermit.setup_sketch_upload_to,
                verbose_name='setup sketch',
            ),
        ),
    ]