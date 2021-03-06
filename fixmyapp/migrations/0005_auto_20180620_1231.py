# Generated by Django 2.0 on 2018-06-20 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fixmyapp', '0004_profile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='category_of_bike',
            field=models.CharField(
                choices=[
                    ('racing_cycle', 'racing cycle'),
                    ('city_bike', 'city bike'),
                    ('mountain_bike', 'mountain bike'),
                    ('e_bike', 'e-bike'),
                    ('cargo_bike', 'cargo bike'),
                    ('e_cargo_bike', 'e-cargo-bike'),
                ],
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name='profile',
            name='usage',
            field=models.PositiveSmallIntegerField(
                choices=[
                    (0, 'never'),
                    (3, 'once per day'),
                    (2, 'once per week'),
                    (1, 'once per month'),
                ]
            ),
        ),
    ]
