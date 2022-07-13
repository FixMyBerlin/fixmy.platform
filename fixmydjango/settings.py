"""
Django settings for fixmydjango project.

Generated by 'django-admin startproject' using Django 2.0.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import datetime
import logging
import os

from corsheaders.defaults import default_headers

from .utils import get_templates_config

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

# Sentry
SENTRY_DSN = os.getenv('SENTRY_DSN', '')
sentry_sdk.init(
    dsn=SENTRY_DSN,
    integrations=[DjangoIntegration()],
    traces_sample_rate=0.0,
    send_default_pii=True,
)

# Logging

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', logging.INFO),
        },
        '': {
            'handlers': ['console'],
            'level': os.getenv('LOG_LEVEL', logging.WARNING),
        },
    },
}


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'set-this-for-production!')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(os.getenv('DEBUG', False))

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'anymail',
    'corsheaders',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.gis',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'djoser',
    'fixmyapp.apps.FixmyappConfig',
    'markdownx',
    'rest_framework',
    'rest_framework_gis',
    'reversion',
    'survey',
    'reports',
    'permits',
    'fahrradparken',
]

MIDDLEWARE = [
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'reversion.middleware.RevisionMiddleware',
    'fixmyapp.middleware.TimezoneMiddleware',
]

ROOT_URLCONF = 'fixmydjango.urls'

AVAILABLE_TEMPLATE_SETS = ('fixmyberlin', 'aachen')
TEMPLATE_SET = os.getenv('TEMPLATE_SET', 'fixmyberlin')
TEMPLATES = get_templates_config(TEMPLATE_SET, BASE_DIR, AVAILABLE_TEMPLATE_SETS)

WSGI_APPLICATION = 'fixmydjango.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.getenv('DATABASE_NAME', 'docker'),
        'USER': os.getenv('DATABASE_USER', 'docker'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD', 'docker'),
        'HOST': os.getenv('DATABASE_HOST', 'db'),
        'PORT': 5432,
    }
}

# Model used for auto-created primary key field
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'
    },
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'de-de'

LOCALE_PATHS = [os.path.join(BASE_DIR, 'locale')]

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

STATIC_URL = os.getenv('STATIC_URL', '/static/')

STATIC_ROOT = '/code/static'


# Request body size
# https://docs.djangoproject.com/en/2.1/ref/settings/#data-upload-max-memory-size

DATA_UPLOAD_MAX_MEMORY_SIZE = 26214400


# Maximum number of parameters per request
# https://docs.djangoproject.com/en/2.1/ref/settings/#data-upload-max-number-fields
DATA_UPLOAD_MAX_NUMBER_FIELDS = int(os.getenv('DATA_UPLOAD_MAX_NUMBER_FIELDS', '1000'))


# CORS headers
# https://github.com/ottoyiu/django-cors-headers

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_HEADERS = list(default_headers) + ['Content-Disposition']


# Amazon S3
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')

AWS_QUERYSTRING_AUTH = bool(os.getenv('AWS_QUERYSTRING_AUTH', False))

AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')

AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME')

AWS_S3_USE_SSL = bool(os.getenv('AWS_S3_USE_SSL', True))

AWS_S3_SIGNATURE_VERSION = os.getenv('AWS_S3_SIGNATURE_VERSION', 's3v4')


# Anymail
# https://anymail.readthedocs.io/en/stable/

EMAIL_BACKEND = os.getenv(
    'EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend'
)

DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'info@fixmyberlin.de')

EMAIL_REPLY_TO = os.getenv('EMAIL_REPLY_TO')

ANYMAIL = {
    'MAILJET_API_KEY': os.getenv('MAILJET_API_KEY', ''),
    'MAILJET_SECRET_KEY': os.getenv('MAILJET_SECRET_KEY', ''),
}

NEWSLETTER_LIST_ID = os.getenv('NEWSLETTER_LIST_ID')


# Mapbox
# https://www.mapbox.com/api-documentation/#uploads

MAPBOX_ACCESS_TOKEN = os.getenv('MAPBOX_ACCESS_TOKEN', '')

MAPBOX_UPLOAD_REGION = os.getenv('MAPBOX_UPLOAD_REGION', 'us-east-1')

MAPBOX_UPLOAD_NAME = {
    'sections': os.getenv('MAPBOX_UPLOAD_NAME_SECTIONS', ''),
    'projects': os.getenv('MAPBOX_UPLOAD_NAME_PROJECTS', ''),
}

MAPBOX_UPLOAD_TILESET = {
    'sections': os.getenv('MAPBOX_UPLOAD_TILESET_SECTIONS', ''),
    'projects': os.getenv('MAPBOX_UPLOAD_TILESET_PROJECTS', ''),
}

MAPBOX_UPLOAD_URL = os.getenv('MAPBOX_UPLOAD_URL', 'https://api.mapbox.com/uploads/v1')

MAPBOX_USERNAME = os.getenv('MAPBOX_USERNAME', '')


# REST Framework
# http://django-rest-framework.org

REST_FRAMEWORK = {
    'COERCE_DECIMAL_TO_STRING': False,
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication'
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer'],
    'DEFAULT_SCHEMA_CLASS': 'rest_framework_gis.schema.GeoFeatureAutoSchema',
}


# Simple JWT
# https://github.com/davesque/django-rest-framework-simplejwt

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': datetime.timedelta(days=180),
    'AUTH_HEADER_TYPES': ('JWT',),
    'REFRESH_TOKEN_LIFETIME': datetime.timedelta(days=720),
}


# Djoser
# https://djoser.readthedocs.io/en/stable/index.html

DJOSER = {
    'PASSWORD_RESET_CONFIRM_URL': os.getenv(
        'PASSWORD_RESET_CONFIRM_URL', 'reset/{uid}/{token}'
    ),
    'PASSWORD_RESET_CONFIRM_FRONTEND_URL': os.getenv(
        'PASSWORD_RESET_CONFIRM_FRONTEND_URL', ''
    ),
    'ACTIVATION_URL': os.getenv('ACTIVATION_URL', 'activate/{uid}/{token}'),
    'ACTIVATION_FRONTEND_URL': os.getenv('ACTIVATION_FRONTEND_URL', ''),
    'SEND_ACTIVATION_EMAIL': bool(os.getenv('SEND_ACTIVATION_EMAIL', False)),
    'EMAIL': {'activation': 'fixmyapp.email.ActivationEmail'},
}


# Use X-Forwarded-Host header
# https://docs.djangoproject.com/en/2.2/ref/settings/#use-x-forwarded-host

USE_X_FORWARDED_HOST = bool(os.getenv('USE_X_FORWARDED_HOST', False))


# Use X-Forwarded-Proto header
# https://docs.djangoproject.com/en/2.2/ref/settings/#secure-proxy-ssl-header

SECURE_PROXY_SSL_HEADER = (
    ('HTTP_X_FORWARDED_PROTO', 'https') if USE_X_FORWARDED_HOST else None
)

# Feature-Toggles

TOGGLE_NEWSLETTER = bool(os.getenv('TOGGLE_NEWSLETTER', False))
TOGGLE_GASTRO_REGISTRATIONS = bool(os.getenv('TOGGLE_GASTRO_REGISTRATIONS', True))
TOGGLE_GASTRO_DIRECT_SIGNUP = bool(os.getenv('TOGGLE_GASTRO_DIRECT_SIGNUP', False))

# Configuration for Gastro-app

GASTRO_RECIPIENT = os.getenv('GASTRO_RECIPIENT', 'aufsicht.sga@ba-fk.berlin.de')
GASTRO_SIGNUPS_OPEN = os.getenv('GASTRO_SIGNUPS_OPEN', None)
GASTRO_SIGNUPS_CLOSE = os.getenv('GASTRO_SIGNUPS_CLOSE', None)

# Configuration for Permits app

# Configures the recipient of event application decision notices
EVENT_RECIPIENT = os.getenv('EVENT_RECIPIENT', 'aufsicht.sga@ba-fk.berlin.de')

# (optional) set these values to something that can be parsed by datetime
# (e.g. iso 8601 date) to configure a time frame outside of which requests to
# the signup endpoint will fail
EVENT_SIGNUPS_OPEN = os.getenv('EVENT_SIGNUPS_OPEN', None)
EVENT_SIGNUPS_CLOSE = os.getenv('EVENT_SIGNUPS_CLOSE', None)

# (optional) set to an email address to add a reply-to header to emails sent
# from the event app
EVENT_REPLY_TO = os.getenv('EVENT_REPLY_TO', None)

# Configuration for reports app

REPORTS_NOTIFICATION_CAMPAIGN = os.getenv('REPORTS_NOTIFICATION_CAMPAIGN', None)
REPORTS_NOTIFICATION_SENDER = os.getenv('REPORTS_NOTIFICATION_SENDER', None)

FRONTEND_URL = os.getenv('FRONTEND_URL', 'https://fixmyberlin.de')

# Configuration for playstreets
PLAYSTREET_RECIPIENT = os.getenv('PLAYSTREET_RECIPIENT', 'info@fixmycity.de')

# Configuration for fahrradparken
FAHRRADPARKEN_REPLY_TO = os.getenv(
    'FAHRRADPARKEN_REPLY_TO', 'radparken@deutschebahn.com'
)
