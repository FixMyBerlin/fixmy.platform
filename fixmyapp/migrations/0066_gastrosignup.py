# Generated by Django 3.0.5 on 2020-05-12 15:44

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fixmyapp', '0065_merge_20200506_1138'),
    ]

    operations = [
        migrations.CreateModel(
            name='GastroSignup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('campaign', models.CharField(max_length=64, verbose_name='campaign')),
                ('name', models.TextField(verbose_name='name')),
                ('email', models.CharField(max_length=255, verbose_name='email')),
                ('address', models.TextField(verbose_name='address')),
                ('geometry', django.contrib.gis.db.models.fields.PointField(srid=4326, verbose_name='geometry')),
                ('seats_requested', models.PositiveIntegerField(verbose_name='requested seats')),
                ('time_requested', models.CharField(choices=[('weekend', 'weekend'), ('week', 'whole week')], max_length=32, verbose_name='time_requested')),
                ('accepts_agreement', models.BooleanField(verbose_name='agreement accepted')),
                ('tos_accepted', models.BooleanField(default=False, verbose_name='tos_accepted')),
            ],
            options={
                'verbose_name': 'gastro_signup',
                'verbose_name_plural': 'gastro_signups',
                'ordering': ['campaign', 'name'],
            },
        ),
    ]
