# Generated by Django 3.0.7 on 2020-10-05 11:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [('reports', '0007_status_notices')]

    operations = [
        migrations.RunSQL(
            """
        BEGIN;
        SELECT setval(pg_get_serial_sequence('"reports_report_origin"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "reports_report_origin";
        SELECT setval(pg_get_serial_sequence('"reports_report"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "reports_report";
        SELECT setval(pg_get_serial_sequence('"reports_statusnotice"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "reports_statusnotice";
        COMMIT;
        """
        )
    ]