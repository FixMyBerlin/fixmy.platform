# Generated by Django 3.1.3 on 2021-04-28 09:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fixmyapp', '0088_gastro_update_2021'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='has_trailer',
            field=models.BooleanField(
                blank=True, null=True, verbose_name='has trailer'
            ),
        ),
    ]
