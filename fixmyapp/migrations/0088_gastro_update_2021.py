# Generated by Django 3.1.3 on 2021-03-18 16:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fixmyapp', '0087_section_accidents'),
    ]

    operations = [
        migrations.AddField(
            model_name='gastrosignup',
            name='followup_accepted',
            field=models.BooleanField(default=False, verbose_name='follow-up accepted'),
        ),
        migrations.AlterField(
            model_name='gastrosignup',
            name='campaign',
            field=models.CharField(
                choices=[
                    ('xhain', 'Xhain Mai 2020'),
                    ('xhain2', 'Xhain Juli 2020'),
                    ('xhain3', 'Xhain Verlängerungen ab Sep 2020'),
                    ('xhain2021', 'Xhain 2021'),
                    ('tempelberg', 'Tempelhof-Schöneberg 2020'),
                ],
                max_length=32,
                verbose_name='campaign',
            ),
        ),
    ]
