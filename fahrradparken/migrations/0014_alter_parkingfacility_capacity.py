# Generated by Django 3.2.4 on 2021-11-30 13:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fahrradparken', '0013_parkingfacilityphoto_is_published'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parkingfacility',
            name='capacity',
            field=models.IntegerField(blank=True, null=True, verbose_name='capacity'),
        ),
    ]
