# Generated by Django 3.1.3 on 2021-02-03 15:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fixmyapp', '0087_section_is_road'),
    ]

    operations = [
        migrations.CreateModel(
            name='SectionAccidents',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='Created date')),
                ('modified_date', models.DateTimeField(auto_now=True, verbose_name='Modified date')),
                ('killed', models.IntegerField(verbose_name='killed')),
                ('severely_injured', models.IntegerField(verbose_name='severely injured')),
                ('slightly_injured', models.IntegerField(verbose_name='slightly injured')),
                ('source', models.TextField(blank=True, null=True, verbose_name='source')),
                ('risk_level', models.PositiveSmallIntegerField(choices=[(2, 'accident blackspot'), (1, 'some accidents'), (0, 'no accidents')], verbose_name='Risiko')),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='accidents', to='fixmyapp.section')),
            ],
            options={
                'verbose_name': 'Section accident data',
                'verbose_name_plural': 'Section accident datasets',
            },
        ),
    ]
