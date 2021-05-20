# Generated by Django 3.1.6 on 2021-05-19 14:08

from django.db import migrations, models
import fixmyapp.models.gastro_signup


class Migration(migrations.Migration):

    dependencies = [
        ('fixmyapp', '0089_replace_deprecated_field'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gastrosignup',
            name='certificate',
            field=models.FileField(
                blank=True,
                max_length=255,
                null=True,
                upload_to=fixmyapp.models.gastro_signup.get_upload_path,
                verbose_name='registration certificate',
            ),
        ),
    ]
