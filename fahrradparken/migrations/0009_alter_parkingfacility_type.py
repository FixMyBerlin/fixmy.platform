# Generated by Django 3.2.4 on 2021-11-12 11:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fahrradparken', '0008_alter_surveystation_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parkingfacility',
            name='type',
            field=models.IntegerField(
                choices=[
                    (0, 'enclosed compound'),
                    (1, 'bicycle locker'),
                    (2, 'bicycle parking tower'),
                ],
                null=True,
            ),
        ),
    ]
