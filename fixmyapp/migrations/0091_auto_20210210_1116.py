# Generated by Django 3.1.3 on 2021-02-10 11:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fixmyapp', '0090_sectionaccidents_side'),
    ]

    operations = [
        migrations.AlterField(
            model_name='section',
            name='street_name',
            field=models.CharField(max_length=255, verbose_name='street name'),
        ),
    ]