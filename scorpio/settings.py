"""
Django settings for scorpio project.

Generated by 'django-admin startproject' using Django 2.0.10.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os

from . import config

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config.DJANGO_SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config.DJANGO_DEBUG

ALLOWED_HOSTS = config.DJANGO_ALLOWED_HOSTS


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'indexer',
    'django_cron',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'scorpio.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR, os.path.join(BASE_DIR, 'indexer', 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'scorpio.wsgi.application'

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": config.SQL_ENGINE,
        "NAME": config.SQL_DATABASE,
        "USER": config.SQL_USER,
        "PASSWORD": config.SQL_PASSWORD,
        "HOST": config.SQL_HOST,
        "PORT": config.SQL_PORT,
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

FIXTURE_DIRS = [os.path.join(BASE_DIR, 'fixtures')]

AUTH_USER_MODEL = 'indexer.User'

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 25
}

# Django cron settings
CRON_CLASSES = [
    "indexer.cron.IndexAll",
    "indexer.cron.IndexAllClean",
    "indexer.cron.IndexAgents",
    "indexer.cron.IndexAgentsClean",
    "indexer.cron.IndexCollections",
    "indexer.cron.IndexCollectionsClean",
    "indexer.cron.IndexObjects",
    "indexer.cron.IndexObjectsClean",
    "indexer.cron.IndexTerms",
    "indexer.cron.IndexTermsClean",
]
DJANGO_CRON_LOCK_BACKEND = "django_cron.backends.lock.file.FileLock"
DJANGO_CRON_LOCKFILE_PATH = config.DJANGO_CRON_LOCKFILE_PATH

# Elasticsearch configuration
ELASTICSEARCH = {
    'default': {
        'hosts': config.ELASTICSEARCH_HOSTS,
        'index': config.ELASTICSEARCH_INDEX,
        'api_key': config.get('ELASTICSEARCH_API_KEY')
    },
}

# Pisces Configs
PISCES = {
    "baseurl": config.PISCES_BASEURL,
    "post_index_path": config.PISCES_POST_INDEX_PATH
}

MAX_OBJECTS = config.MAX_OBJECTS
