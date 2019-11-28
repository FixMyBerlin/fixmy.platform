# Generated by Django 2.0.12 on 2019-11-27 15:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0004_auto_20191115_0903'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Survey',
            new_name='Session',
        ),
        migrations.AlterModelOptions(
            name='session',
            options={'verbose_name': 'session', 'verbose_name_plural': 'sessions'},
        ),
        migrations.RenameField(
            model_name='rating',
            old_name='survey',
            new_name='session',
        ),
        migrations.AlterField(
            model_name='session',
            name='id',
            field=models.UUIDField(primary_key=True, serialize=False, verbose_name='id'),
        ),
    ]
