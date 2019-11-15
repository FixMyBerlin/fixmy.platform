# Generated by Django 2.0.12 on 2019-10-23 12:24

import django.contrib.gis.db.models.fields
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import markdownx.models


class Migration(migrations.Migration):

    dependencies = [
        ('fixmyapp', '0048_project_alert_date'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='photo',
            options={'verbose_name': 'photo', 'verbose_name_plural': 'photos'},
        ),
        migrations.AlterModelOptions(
            name='profile',
            options={'verbose_name': 'profile', 'verbose_name_plural': 'profiles'},
        ),
        migrations.AlterModelOptions(
            name='project',
            options={'verbose_name': 'project', 'verbose_name_plural': 'projects'},
        ),
        migrations.AlterModelOptions(
            name='question',
            options={'ordering': ('text',), 'verbose_name': 'question', 'verbose_name_plural': 'questions'},
        ),
        migrations.AlterModelOptions(
            name='report',
            options={'verbose_name': 'report', 'verbose_name_plural': 'reports'},
        ),
        migrations.AlterModelOptions(
            name='section',
            options={'verbose_name': 'section', 'verbose_name_plural': 'sections'},
        ),
        migrations.AlterField(
            model_name='profile',
            name='age',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='age'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='category_of_bike',
            field=models.CharField(blank=True, choices=[('racing_cycle', 'racing cycle'), ('city_bike', 'city bike'), ('mountain_bike', 'mountain bike'), ('e_bike', 'e-bike'), ('cargo_bike', 'cargo bike'), ('e_cargo_bike', 'e-cargo-bike')], max_length=20, null=True, verbose_name='category of bike'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='has_trailer',
            field=models.NullBooleanField(verbose_name='has trailer'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='postal_code',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='postal code'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='security',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='security'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='sex',
            field=models.CharField(blank=True, choices=[('m', 'male'), ('f', 'female'), ('o', 'other')], max_length=1, null=True, verbose_name='sex'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='speed',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='speed'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='usage',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(0, 'never'), (3, 'once per day'), (2, 'once per week'), (1, 'once per month')], null=True, verbose_name='usage'),
        ),
        migrations.AlterField(
            model_name='project',
            name='alert_date',
            field=models.DateField(blank=True, null=True, verbose_name='alert date'),
        ),
        migrations.AlterField(
            model_name='project',
            name='borough',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='borough'),
        ),
        migrations.AlterField(
            model_name='project',
            name='category',
            field=models.CharField(blank=True, choices=[('new cycling infrastructure', 'new cycling infrastructure'), ('renovation of cycling infrastructure', 'renovation of cycling infrastructure'), ('bike street', 'bike street'), ('modification of junction', 'modification of junction'), ('bike parking', 'bike parking'), ('crossing aid', 'crossing aid'), ('modification of cross section', 'modification of cross section'), ('new street', 'new street'), ('shared space', 'shared space'), ('miscellaneous', 'miscellaneous')], max_length=40, null=True, verbose_name='category'),
        ),
        migrations.AlterField(
            model_name='project',
            name='construction_completed',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='construction completed'),
        ),
        migrations.AlterField(
            model_name='project',
            name='construction_started',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='construction started'),
        ),
        migrations.AlterField(
            model_name='project',
            name='costs',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='costs'),
        ),
        migrations.AlterField(
            model_name='project',
            name='cross_section',
            field=models.ImageField(blank=True, null=True, upload_to='photos', verbose_name='cross section'),
        ),
        migrations.AlterField(
            model_name='project',
            name='description',
            field=markdownx.models.MarkdownxField(verbose_name='description'),
        ),
        migrations.AlterField(
            model_name='project',
            name='draft_submitted',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='draft submitted'),
        ),
        migrations.AlterField(
            model_name='project',
            name='external_url',
            field=models.URLField(blank=True, null=True, verbose_name='external URL'),
        ),
        migrations.AlterField(
            model_name='project',
            name='faq',
            field=models.ManyToManyField(blank=True, to='fixmyapp.Question', verbose_name='faq'),
        ),
        migrations.AlterField(
            model_name='project',
            name='geometry',
            field=django.contrib.gis.db.models.fields.GeometryField(blank=True, null=True, srid=4326, verbose_name='geometry'),
        ),
        migrations.AlterField(
            model_name='project',
            name='length',
            field=models.IntegerField(blank=True, null=True, verbose_name='length'),
        ),
        migrations.AlterField(
            model_name='project',
            name='phase',
            field=models.CharField(blank=True, choices=[('draft', 'draft'), ('planning', 'planning'), ('review', 'review'), ('inactive', 'inactive'), ('execution', 'execution'), ('ready', 'ready'), ('miscellaneous', 'miscellaneous')], max_length=30, null=True, verbose_name='phase'),
        ),
        migrations.AlterField(
            model_name='project',
            name='project_key',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='project key'),
        ),
        migrations.AlterField(
            model_name='project',
            name='published',
            field=models.BooleanField(default=True, verbose_name='published'),
        ),
        migrations.AlterField(
            model_name='project',
            name='responsible',
            field=models.CharField(max_length=256, verbose_name='responsible'),
        ),
        migrations.AlterField(
            model_name='project',
            name='short_description',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='short description'),
        ),
        migrations.AlterField(
            model_name='project',
            name='side',
            field=models.PositiveSmallIntegerField(choices=[(0, 'right'), (1, 'left'), (2, 'both')], verbose_name='side'),
        ),
        migrations.AlterField(
            model_name='project',
            name='status',
            field=models.CharField(blank=True, choices=[('unknown', 'unknown'), ('idea', 'idea'), ('preliminary planning', 'preliminary planning'), ('blueprint planning', 'blueprint planning'), ('approval planning', 'approval planning'), ('examination', 'examination'), ('execution planning', 'execution planning'), ('preparation of awarding', 'preparation of awarding'), ('awarding', 'awarding'), ('application for construction site', 'application for construction site'), ('execution of construction work', 'execution of construction work'), ('ready', 'ready'), ('review', 'review'), ('cancelled', 'cancelled')], max_length=40, null=True, verbose_name='status'),
        ),
        migrations.AlterField(
            model_name='project',
            name='street_name',
            field=models.CharField(max_length=100, verbose_name='street name'),
        ),
        migrations.AlterField(
            model_name='project',
            name='title',
            field=models.CharField(max_length=256, verbose_name='title'),
        ),
        migrations.AlterField(
            model_name='report',
            name='address',
            field=models.TextField(blank=True, null=True, verbose_name='address'),
        ),
        migrations.AlterField(
            model_name='report',
            name='description',
            field=models.CharField(blank=True, max_length=400, null=True, verbose_name='description'),
        ),
        migrations.AlterField(
            model_name='report',
            name='details',
            field=django.contrib.postgres.fields.jsonb.JSONField(verbose_name='details'),
        ),
        migrations.AlterField(
            model_name='report',
            name='geometry',
            field=django.contrib.gis.db.models.fields.PointField(srid=4326, verbose_name='geometry'),
        ),
        migrations.AlterField(
            model_name='report',
            name='published',
            field=models.BooleanField(default=True, verbose_name='published'),
        ),
        migrations.AlterField(
            model_name='report',
            name='status',
            field=models.CharField(blank=True, choices=[('new', 'new'), ('verification', 'verification'), ('accepted', 'accepted'), ('rejected', 'rejected'), ('done', 'done')], default='new', max_length=20, null=True, verbose_name='status'),
        ),
        migrations.AlterField(
            model_name='report',
            name='status_reason',
            field=models.TextField(blank=True, null=True, verbose_name='reason for status'),
        ),
        migrations.AlterField(
            model_name='section',
            name='borough',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='borough'),
        ),
        migrations.AlterField(
            model_name='section',
            name='geometry',
            field=django.contrib.gis.db.models.fields.MultiLineStringField(null=True, srid=4326, verbose_name='geometry'),
        ),
        migrations.AlterField(
            model_name='section',
            name='street_category',
            field=models.PositiveSmallIntegerField(null=True, verbose_name='street category'),
        ),
        migrations.AlterField(
            model_name='section',
            name='street_name',
            field=models.CharField(max_length=100, verbose_name='street name'),
        ),
        migrations.AlterField(
            model_name='section',
            name='suffix',
            field=models.CharField(blank=True, max_length=3, null=True, verbose_name='suffix'),
        ),
    ]