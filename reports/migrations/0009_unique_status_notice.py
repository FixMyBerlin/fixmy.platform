# Generated by Django 3.0.7 on 2020-10-12 09:25

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('reports', '0008_fix_pk_sequence'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='statusnotice',
            unique_together={('report_id', 'user_id', 'status', 'date')},
        )
    ]