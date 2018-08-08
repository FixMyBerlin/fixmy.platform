# Generated by Django 2.0 on 2018-08-08 06:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fixmyapp', '0027_planningsection_street_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='planning',
            name='category',
            field=models.CharField(blank=True, choices=[('new cycling infrastructure', 'new cycling infrastructure'), ('renovation of cycling infrastructure', 'renovation of cycling infrastructure'), ('bike street', 'bike street'), ('modification of junction', 'modification of junction'), ('bike parking', 'bike parking'), ('crossing aid', 'crossing aid'), ('modification of cross section', 'modification of cross section'), ('miscellaneous', 'miscellaneous')], max_length=40, null=True),
        ),
    ]
