# Generated by Django 2.0 on 2018-06-19 12:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fixmyapp', '0003_planningsection_progress'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('age', models.PositiveSmallIntegerField()),
                ('category_of_bike', models.CharField(max_length=20)),
                ('has_trailer', models.BooleanField()),
                ('postal_code', models.CharField(max_length=5)),
                (
                    'sex',
                    models.CharField(
                        choices=[('m', 'male'), ('f', 'female'), ('o', 'other')],
                        max_length=1,
                    ),
                ),
                ('speed', models.PositiveSmallIntegerField()),
                ('security', models.PositiveSmallIntegerField()),
                ('usage', models.PositiveSmallIntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
