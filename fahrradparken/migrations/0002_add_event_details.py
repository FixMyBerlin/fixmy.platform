# Generated by Django 3.1.11 on 2021-07-01 13:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fahrradparken', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventsignup',
            name='event_date',
            field=models.CharField(
                default='', max_length=255, verbose_name='event date'
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='eventsignup',
            name='event_time',
            field=models.CharField(
                default='', max_length=255, verbose_name='event time'
            ),
            preserve_default=False,
        ),
    ]
