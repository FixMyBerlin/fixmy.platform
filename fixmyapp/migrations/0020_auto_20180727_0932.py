# Generated by Django 2.0 on 2018-07-27 09:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fixmyapp', '0019_auto_20180727_0859'),
    ]

    operations = [
        migrations.RenameField(
            model_name='planning', old_name='phase', new_name='status',
        ),
    ]
