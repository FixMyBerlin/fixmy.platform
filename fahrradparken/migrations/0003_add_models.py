# Generated by Django 3.2.4 on 2021-08-18 14:22

import django.contrib.gis.db.models.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import fahrradparken.models


class Migration(migrations.Migration):

    dependencies = [
        ('fahrradparken', '0002_add_event_details'),
    ]

    operations = [
        migrations.CreateModel(
            name='Station',
            fields=[
                (
                    'created_date',
                    models.DateTimeField(
                        auto_now_add=True, verbose_name='Created date'
                    ),
                ),
                (
                    'modified_date',
                    models.DateTimeField(auto_now=True, verbose_name='Modified date'),
                ),
                (
                    'id',
                    models.IntegerField(
                        primary_key=True, serialize=False, verbose_name='station number'
                    ),
                ),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                (
                    'location',
                    django.contrib.gis.db.models.fields.PointField(
                        srid=4326, verbose_name='geometry'
                    ),
                ),
                (
                    'travellers',
                    models.IntegerField(
                        choices=[
                            (0, 'No data available'),
                            (1, 'less than 100'),
                            (2, '100-300'),
                            (3, '301-1,000'),
                            (4, '1,001-3,000'),
                            (5, '3001-10,000'),
                            (6, '10,001-50,000'),
                            (7, 'more than 50,000'),
                        ],
                        verbose_name='traveller count',
                    ),
                ),
                (
                    'post_code',
                    models.CharField(
                        blank=True, max_length=16, null=True, verbose_name='post code'
                    ),
                ),
                (
                    'is_long_distance',
                    models.BooleanField(
                        default=False, verbose_name='long distance station'
                    ),
                ),
                (
                    'is_light_rail',
                    models.BooleanField(
                        default=False, verbose_name='light rail station'
                    ),
                ),
                (
                    'is_subway',
                    models.BooleanField(default=False, verbose_name='subway station'),
                ),
                (
                    'community',
                    models.CharField(
                        blank=True, max_length=255, null=True, verbose_name='community'
                    ),
                ),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SurveyBicycleUsage',
            fields=[
                (
                    'created_date',
                    models.DateTimeField(
                        auto_now_add=True, verbose_name='Created date'
                    ),
                ),
                (
                    'modified_date',
                    models.DateTimeField(auto_now=True, verbose_name='Modified date'),
                ),
                (
                    'session',
                    models.UUIDField(
                        primary_key=True, serialize=False, verbose_name='session'
                    ),
                ),
                (
                    'survey_version',
                    models.IntegerField(default=1, verbose_name='survey version'),
                ),
                (
                    'frequency',
                    models.IntegerField(
                        choices=[
                            (0, '(almost) daily'),
                            (1, '1-3 days a week'),
                            (2, '1-3 days a month'),
                            (3, 'less than once a month'),
                            (4, '(almost) never'),
                        ],
                        verbose_name='frequency',
                    ),
                ),
                (
                    'reasons',
                    models.CharField(blank=True, max_length=32, verbose_name='reasons'),
                ),
                (
                    'reason_custom',
                    models.TextField(blank=True, verbose_name='reasons (free text)'),
                ),
                (
                    'duration',
                    models.IntegerField(
                        choices=[
                            (0, 'less than 5 minutes'),
                            (1, '5-10 minutes'),
                            (2, '10-15 minutes'),
                            (3, '15-20 minutes'),
                            (4, '20-25 minutes'),
                            (5, '25-30 minutes'),
                            (6, '30 minutes and above'),
                        ],
                        verbose_name='duration',
                    ),
                ),
                ('with_children', models.BooleanField(verbose_name='with children')),
                (
                    'purpose',
                    models.IntegerField(
                        choices=[
                            (0, 'work'),
                            (1, 'work related'),
                            (2, 'education'),
                            (3, 'shopping'),
                            (4, 'errands'),
                            (5, 'leisure'),
                            (6, 'transport of persons'),
                            (7, 'other'),
                        ],
                        verbose_name='purpose',
                    ),
                ),
                (
                    'rating_racks',
                    models.IntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(limit_value=0),
                            django.core.validators.MaxValueValidator(limit_value=5),
                        ],
                        verbose_name='bicycle racks',
                    ),
                ),
                (
                    'rating_sheltered_racks',
                    models.IntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(limit_value=0),
                            django.core.validators.MaxValueValidator(limit_value=5),
                        ],
                        verbose_name='sheltered bicycle racks',
                    ),
                ),
                (
                    'rating_bike_box',
                    models.IntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(limit_value=0),
                            django.core.validators.MaxValueValidator(limit_value=5),
                        ],
                        verbose_name='bicycle box',
                    ),
                ),
                (
                    'rating_bike_quality',
                    models.IntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(limit_value=0),
                            django.core.validators.MaxValueValidator(limit_value=5),
                        ],
                        verbose_name='bicycle quality',
                    ),
                ),
                (
                    'rating_road_network',
                    models.IntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(limit_value=0),
                            django.core.validators.MaxValueValidator(limit_value=5),
                        ],
                        verbose_name='road network',
                    ),
                ),
                (
                    'rating_train_network',
                    models.IntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(limit_value=0),
                            django.core.validators.MaxValueValidator(limit_value=5),
                        ],
                        verbose_name='train network',
                    ),
                ),
                (
                    'rating_services',
                    models.IntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(limit_value=0),
                            django.core.validators.MaxValueValidator(limit_value=5),
                        ],
                        verbose_name='services',
                    ),
                ),
                (
                    'price',
                    models.IntegerField(
                        choices=[
                            (0, 'less than 5€'),
                            (1, '5-10€'),
                            (2, '10-15€'),
                            (3, '15-20€'),
                            (4, 'more than 20€'),
                        ],
                        null=True,
                        verbose_name='price',
                    ),
                ),
                (
                    'age',
                    models.IntegerField(
                        choices=[
                            (0, 'under 18'),
                            (1, '18-24'),
                            (2, '25-29'),
                            (3, '30-39'),
                            (4, '40-49'),
                            (5, '50-64'),
                            (6, '65-74'),
                            (7, '75 and above'),
                        ],
                        verbose_name='age',
                    ),
                ),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SurveyStation',
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
                    'created_date',
                    models.DateTimeField(
                        auto_now_add=True, verbose_name='Created date'
                    ),
                ),
                (
                    'modified_date',
                    models.DateTimeField(auto_now=True, verbose_name='Modified date'),
                ),
                ('session', models.UUIDField(verbose_name='session')),
                (
                    'survey_version',
                    models.IntegerField(default=1, verbose_name='survey version'),
                ),
                ('npr', models.IntegerField(verbose_name='net promoter rating')),
                (
                    'annoyances',
                    models.CharField(max_length=32, verbose_name='annoyances'),
                ),
                (
                    'annoyance_custom',
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name='annoyance custom',
                    ),
                ),
                (
                    'requested_location',
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name='requested bike parking location',
                    ),
                ),
                (
                    'photo',
                    models.FileField(
                        blank=True,
                        max_length=255,
                        null=True,
                        upload_to=fahrradparken.models.SurveyStation.photo_upload_to,
                        verbose_name='photo',
                    ),
                ),
                (
                    'photo_terms_accepted',
                    models.DateTimeField(
                        blank=True,
                        null=True,
                        verbose_name='photo upload terms accepted',
                    ),
                ),
                (
                    'photo_description',
                    models.TextField(
                        blank=True, null=True, verbose_name='photo description'
                    ),
                ),
                (
                    'station',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='survey_responses',
                        to='fahrradparken.station',
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name='surveystation',
            constraint=models.UniqueConstraint(
                fields=('session', 'station_id'), name='unique-session-station'
            ),
        ),
    ]
