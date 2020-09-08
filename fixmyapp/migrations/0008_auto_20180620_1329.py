# Generated by Django 2.0 on 2018-06-20 13:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fixmyapp', '0007_auto_20180620_1250'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='age',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='category_of_bike',
            field=models.CharField(
                blank=True,
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
            name='has_trailer',
            field=models.NullBooleanField(),
        ),
        migrations.AlterField(
            model_name='profile',
            name='postal_code',
            field=models.CharField(blank=True, max_length=5),
        ),
        migrations.AlterField(
            model_name='profile',
            name='security',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='sex',
            field=models.CharField(
                blank=True,
                choices=[('m', 'male'), ('f', 'female'), ('o', 'other')],
                max_length=1,
            ),
        ),
        migrations.AlterField(
            model_name='profile',
            name='speed',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='usage',
            field=models.PositiveSmallIntegerField(
                blank=True,
                choices=[
                    (0, 'never'),
                    (3, 'once per day'),
                    (2, 'once per week'),
                    (1, 'once per month'),
                ],
                null=True,
            ),
        ),
    ]
