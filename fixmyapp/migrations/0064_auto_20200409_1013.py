# Generated by Django 3.0.5 on 2020-04-09 10:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fixmyapp', '0063_auto_20200318_1152'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bikestands',
            name='fee_acceptable',
            field=models.BooleanField(default=False, verbose_name='fee_acceptable'),
        ),
    ]
