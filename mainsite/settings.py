"""
Django settings for mainsite project.

Generated by 'django-admin startproject' using Django 2.0.dev20170120074947.
"""
# from mainsite.privates import *
import os
from neomodel import db
from neomodel import config as neoconfig
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

"""
Do change the following as pleased, this specifies the connection to the neomodel
"""
# Required for the neo4j connection2
#                               <user>:<password>@<host>:<port>
neoconfig.DATABASE_URL = 'bolt://neo4j:neo4j@localhost:7687'

# Key used for the encryption
FERNET_KEYS = [
    "b'dU67lGCoPdl8X-cThqNVseuQslyc47zDeAC8J3Lalx8='"
]
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'a324$nlf!=n(o2+=sts(@+k2o%x06g@$le9sn-za=2+4rkzjd+'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
# Allowed hosts
ALLOWED_HOSTS = ["127.0.0.1","localhost"]
# CSRF required whitelisting
CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = (
    'localhost',
    '127.0.0.1'
)

# Used for printing tests
NOSE_ARGS = ['--nocapture',
             '--nologcapture',]
# Application definition
INSTALLED_APPS = [
    'django_neomodel',
    'corsheaders',
    'popclick.apps.PopclickConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions'
]
# Required middlew
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
# Main site
ROOT_URLCONF = 'mainsite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'mainsite.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

GRAPH_MODELS = {
  'all_applications': True,
  'group_models': True,
}

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
# https://docs.djangoproject.com/en/dev/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/dev/howto/static-files/

STATIC_URL = '/static/'
