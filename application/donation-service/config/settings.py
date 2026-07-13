"""
Django settings for the donation-service.

Owns donation requests and their donated-medicine line items. Donor and
NGO details are denormalized at request-creation time from user-service;
medicine lists are read from medicine-service. Authentication comes from
the signed-cookie session issued by user-service.
"""

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
# Must be identical across all services: it signs the shared session cookie.
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-py&)x3_w@v$b(7(z8y+t%kkob#oh4$nvp91i=@2raokn(mx!r=',
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'DonationRequestSystem.apps.DonationrequestsystemConfig',
    'health.apps.HealthConfig',
    'common',
    'crispy_forms',
    'crispy_bootstrap4',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'common.middleware.SessionUserMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'common.context_processors.user',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database

DB_ENGINE = os.environ.get('DB_ENGINE', 'mysql')

if DB_ENGINE == 'sqlite3':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.environ.get('DB_NAME', str(BASE_DIR / 'db.sqlite3')),
        }
    }
else:
    import pymysql

    # Ensure pymysql is used as MySQLdb
    pymysql.install_as_MySQLdb()

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ.get('DB_NAME', 'medicine_donation'),
            'USER': os.environ.get('DB_USER', 'admin'),
            'PASSWORD': os.environ.get('DB_PASSWORD'),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '3306'),
        }
    }


# Sessions / messages are cookie-based so every service can read them
# without a shared session store.

SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'


# Internationalization

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

# Default primary key field type

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Login pages live on user-service; routing happens at the gateway.
LOGIN_URL = '/accounts/login/'

# Internal API endpoints of the services this one depends on.
USER_SERVICE_URL = os.environ.get('USER_SERVICE_URL', 'http://user-service')
MEDICINE_SERVICE_URL = os.environ.get('MEDICINE_SERVICE_URL', 'http://medicine-service')

# Shared secret protecting the internal service-to-service API.
INTERNAL_API_TOKEN = os.environ.get('INTERNAL_API_TOKEN', 'insecure-internal-token')
