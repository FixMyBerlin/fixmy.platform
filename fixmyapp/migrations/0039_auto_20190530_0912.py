# Generated by Django 2.0.8 on 2019-05-30 09:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fixmyapp', '0038_report_published'),
    ]

    operations = [
        migrations.AlterField(
            model_name='planning',
            name='phase',
            field=models.CharField(blank=True, choices=[('draft', 'draft'), ('planning', 'planning'), ('review', 'review'), ('inactive', 'inactive'), ('execution', 'execution'), ('ready', 'ready'), ('miscellaneous', 'miscellaneous')], max_length=30, null=True),
        ),
    ]