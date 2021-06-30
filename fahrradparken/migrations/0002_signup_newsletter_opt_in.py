# Generated by Django 3.1.11 on 2021-06-30 07:18

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('fahrradparken', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='signup',
            name='newsletter_opt_in',
            field=models.UUIDField(
                default=uuid.uuid4,
                editable=False,
                verbose_name='newsletter opt in code',
            ),
        ),
    ]
