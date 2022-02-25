# Generated by Django 3.2.4 on 2022-02-16 10:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fixmyapp', '0091_playstreets_boekhstrasse'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gastrosignup',
            name='campaign',
            field=models.CharField(choices=[
                ('xhain', 'Xhain Mai 2020'), 
                ('xhain2', 'Xhain Juli 2020'), 
                ('xhain3', 'Xhain Verlängerungen ab Sep 2020'), 
                ('xhain2021', 'Xhain 2021'), 
                ('xhain2022', 'Xhain 2022'), 
                ('tempelberg', 'Tempelhof-Schöneberg 2020')
            ], max_length=32, verbose_name='campaign'),
        ),
    ]