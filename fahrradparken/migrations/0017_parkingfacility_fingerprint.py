# Generated by Django 3.2.5 on 2021-12-11 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fahrradparken', '0016_auto_20211209_1618'),
    ]

    operations = [
        migrations.AddField(
            model_name='parkingfacility',
            name='fingerprint',
            field=models.CharField(
                blank=True, max_length=64, null=True, verbose_name='fingerprint'
            ),
        ),
    ]
