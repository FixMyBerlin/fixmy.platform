# Generated by Django 2.0 on 2018-03-22 11:32

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fixmyapp', '0002_auto_20180322_1130'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kanten',
            name='geom',
            field=django.contrib.gis.db.models.fields.MultiLineStringField(srid=4326),
        ),
    ]
