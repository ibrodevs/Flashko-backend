import os
from pathlib import Path
from datetime import timedelta
import dj_database_url
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file
load_dotenv(BASE_DIR / '.env')

# Quick-start development settings - unsuitable for production
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-flashcards-quiz-web-app-secret-key-2026')

DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 't')

# Allow all hosts or custom list so everyone can access (PythonAnywhere, custom domains, localhost)
allowed_hosts_env = os.getenv('ALLOWED_HOSTS', '*').strip()
if allowed_hosts_env == '*' or not allowed_hosts_env:
    ALLOWED_HOSTS = ['*']
else:
    ALLOWED_HOSTS = [h.strip() for h in allowed_hosts_env.split(',') if h.strip()]
    if '.pythonanywhere.com' not in allowed_hosts_env:
        ALLOWED_HOSTS.append('.pythonanywhere.com')

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
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',

    # Local apps
    'apps.accounts',
    'apps.flashcards',
    'apps.quiz',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
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
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database configuration:
# 1. If DATABASE_URL is set (PostgreSQL/MySQL), dj_database_url is used.
# 2. Otherwise falls back to SQLite, perfect for PythonAnywhere free tier out of the box!
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.strip():
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL.strip(),
            conn_max_age=600,
            ssl_require=False if DEBUG else os.getenv('DB_SSL_REQUIRE', 'False').lower() in ('true', '1', 't')
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 6,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'apps.accounts.authentication.CustomJWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
}

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# Cookie Settings for Refresh Token
JWT_AUTH_REFRESH_COOKIE = 'refresh_token'
JWT_AUTH_COOKIE_SECURE = os.getenv('JWT_AUTH_COOKIE_SECURE', 'False' if DEBUG else 'True').lower() in ('true', '1', 't')
JWT_AUTH_COOKIE_HTTP_ONLY = True
# Cross-origin (e.g. Vercel calling PythonAnywhere) requires SameSite=None and Secure=True in production
JWT_AUTH_COOKIE_SAMESITE = os.getenv('JWT_AUTH_COOKIE_SAMESITE', 'Lax' if DEBUG else 'None')
JWT_AUTH_COOKIE_PATH = '/'

# CORS Configuration: allow all origins so any client/frontend can make requests
CORS_ALLOW_ALL_ORIGINS = os.getenv('CORS_ALLOW_ALL_ORIGINS', 'True').lower() in ('true', '1', 't')
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# CSRF Configuration
csrf_origins_env = os.getenv('CSRF_TRUSTED_ORIGINS', '')
if csrf_origins_env:
    CSRF_TRUSTED_ORIGINS = [o.strip() for o in csrf_origins_env.split(',') if o.strip()]
else:
    CSRF_TRUSTED_ORIGINS = [
        'http://localhost:3000',
        'http://127.0.0.1:3000',
        'https://*.pythonanywhere.com',
        'https://*.vercel.app',
    ]

# Internationalization
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
