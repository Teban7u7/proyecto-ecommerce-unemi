"""
Django settings for Licorería Virtual Backend.
Nuvei/Paymentez Ecuador Integration
"""

import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
import dj_database_url

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'dev-secret-key-change-in-production')
DEBUG = os.getenv('DJANGO_DEBUG', 'True').lower() == 'true'
ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    # Local apps
    'apps.accounts',
    'apps.products',
    'apps.orders',
    'apps.store_config',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
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
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL', 'sqlite:///db.sqlite3'),
        conn_max_age=600,
    )
}

# Auth
AUTH_USER_MODEL = 'accounts.CustomUser'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# JWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=6),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# CORS
CORS_ALLOWED_ORIGINS = os.getenv(
    'CORS_ALLOWED_ORIGINS',
    'http://localhost:3000,http://localhost:3001,http://localhost:5173'
).split(',')
CORS_ALLOW_CREDENTIALS = True

# Internationalization
LANGUAGE_CODE = 'es-ec'
TIME_ZONE = 'America/Guayaquil'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

# Media
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =============================================================================
# NUVEI / PAYMENTEZ CONFIGURATION
# =============================================================================
NUVEI_CONFIG = {
    'STG': {
        'CCAPI_URL': 'https://ccapi-stg.paymentez.com',
        'NOCCAPI_URL': 'https://noccapi-stg.paymentez.com',
        'APP_CODE_CLIENT': os.getenv('NUVEI_APP_CODE_CLIENT_STG', 'TEBANSTG-EC-CLIENT'),
        'APP_KEY_CLIENT': os.getenv('NUVEI_APP_KEY_CLIENT_STG', ''),
        'APP_CODE_SERVER': os.getenv('NUVEI_APP_CODE_SERVER_STG', 'TEBANSTG-EC-SERVER'),
        'APP_KEY_SERVER': os.getenv('NUVEI_APP_KEY_SERVER_STG', ''),
    },
    'PROD': {
        'CCAPI_URL': 'https://ccapi.paymentez.com',
        'NOCCAPI_URL': 'https://noccapi.paymentez.com',
        'APP_CODE_CLIENT': os.getenv('NUVEI_APP_CODE_CLIENT_PROD', ''),
        'APP_KEY_CLIENT': os.getenv('NUVEI_APP_KEY_CLIENT_PROD', ''),
        'APP_CODE_SERVER': os.getenv('NUVEI_APP_CODE_SERVER_PROD', ''),
        'APP_KEY_SERVER': os.getenv('NUVEI_APP_KEY_SERVER_PROD', ''),
    },
}

# Node.js Payment Service
PAYMENT_SERVICE_URL = os.getenv('PAYMENT_SERVICE_URL', 'http://localhost:3001')
PAYMENT_SERVICE_SECRET = os.getenv('PAYMENT_SERVICE_SECRET', 'internal-shared-secret')

# WhatsApp
WHATSAPP_BUSINESS_NUMBER = os.getenv('WHATSAPP_BUSINESS_NUMBER', '593XXXXXXXXX')
