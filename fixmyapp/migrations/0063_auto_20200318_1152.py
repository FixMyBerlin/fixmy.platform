# Generated by Django 2.2.10 on 2020-03-18 11:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fixmyapp', '0062_auto_20200310_1650'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bikestands',
            name='fee_acceptable',
            field=models.NullBooleanField(verbose_name='fee_acceptable'),
        ),
        migrations.AlterField(
            model_name='bikestands',
            name='number',
            field=models.PositiveSmallIntegerField(verbose_name='number'),
        ),
    ]
