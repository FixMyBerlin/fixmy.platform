# Generated by Django 3.0.7 on 2020-09-15 13:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [('reports', '0005_report_user_reference')]

    operations = [
        migrations.AddField(
            model_name='report',
            name='origin',
            field=models.ManyToManyField(
                blank=True, related_name='plannings', to='reports.Report'
            ),
        )
    ]