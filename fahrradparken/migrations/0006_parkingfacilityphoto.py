# Generated by Django 3.2.4 on 2021-10-02 09:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        (
            'fahrradparken',
            '0005_parkingfacility_parkingfacilitycondition_parkingfacilityoccupancy',
        ),
    ]

    operations = [
        migrations.CreateModel(
            name='ParkingFacilityPhoto',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'description',
                    models.TextField(blank=True, null=True, verbose_name='description'),
                ),
                (
                    'src',
                    models.ImageField(
                        upload_to='fahrradparken/parking-facilities',
                        verbose_name='file',
                    ),
                ),
                (
                    'terms_accepted',
                    models.DateTimeField(
                        blank=True, null=True, verbose_name='upload terms accepted'
                    ),
                ),
                (
                    'parking_facility',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='photos',
                        to='fahrradparken.parkingfacility',
                    ),
                ),
            ],
            options={
                'verbose_name': 'photo',
            },
        ),
    ]
