# Generated by Django 2.0.12 on 2020-01-15 15:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fixmyapp', '0054_auto_20191204_1320'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='construction_completed_date',
            field=models.DateField(blank=True, null=True, verbose_name='construction completed date'),
        ),
    ]
