# Generated by Django 2.0 on 2018-08-08 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fixmyapp', '0029_auto_20180808_0732'),
    ]

    operations = [
        migrations.AlterField(
            model_name='planning',
            name='status',
            field=models.CharField(
                blank=True,
                choices=[
                    ('unknown', 'unknown'),
                    ('idea', 'idea'),
                    ('preliminary planning', 'preliminary planning'),
                    ('blueprint planning', 'blueprint planning'),
                    ('approval planning', 'approval planning'),
                    ('examination', 'examination'),
                    ('execution planning', 'execution planning'),
                    ('preparation of awarding', 'preparation of awarding'),
                    ('awarding', 'awarding'),
                    (
                        'application for construction site',
                        'application for construction site',
                    ),
                    (
                        'execution of construction work',
                        'execution of construction work',
                    ),
                    ('ready', 'ready'),
                    ('review', 'review'),
                    ('cancelled', 'cancelled'),
                ],
                max_length=40,
                null=True,
            ),
        ),
    ]
