# Generated by Django 3.0.7 on 2020-08-06 11:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [('fixmyapp', '0081_auto_20200804_1222')]

    operations = [
        migrations.AlterField(
            model_name='gastrosignup',
            name='campaign',
            field=models.CharField(
                choices=[
                    ('xhain', 'XHain Mai 2020'),
                    ('xhain2', 'XHain Juli 2020'),
                    ('xhain3', 'XHain Verlängerungen ab Sep 2020'),
                    ('tempelberg', 'Tempelhof-Schöneberg 2020'),
                ],
                max_length=32,
                verbose_name='campaign',
            ),
        )
    ]
