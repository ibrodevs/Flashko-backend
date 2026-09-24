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

# Allow hosts for PythonAnywhere and local development
ALLOWED_HOSTS = [
    'flashkobackend21.pythonanywhere.com',
    '.pythonanywhere.com',
    'localhost',
    '127.0.0.1',
    '[::1]',
]
extra_hosts = os.getenv('ALLOWED_HOSTS', '')
if extra_hosts and extra_hosts != '*':
    for h in extra_hosts.split(','):
        if h.strip() and h.strip() not in ALLOWED_HOSTS:
            ALLOWED_HOSTS.append(h.strip())
elif extra_hosts == '*':
    ALLOWED_HOSTS = ['*']

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
# In cross-site production (Vercel https://flashko-ibro.vercel.app -> PythonAnywhere https://flashkobackend21.pythonanywhere.com),
# browsers require SameSite='None' and Secure=True.
JWT_AUTH_COOKIE_SECURE = os.getenv('JWT_AUTH_COOKIE_SECURE', 'True').lower() in ('true', '1', 't')
JWT_AUTH_COOKIE_HTTP_ONLY = True
JWT_AUTH_COOKIE_SAMESITE = os.getenv('JWT_AUTH_COOKIE_SAMESITE', 'None')
JWT_AUTH_COOKIE_PATH = '/'

# CORS Configuration: allow ONLY our frontend and local development
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    'https://flashko-ibro.vercel.app',
    'https://flashkobackend21.pythonanywhere.com',
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]

# Allow any Vercel preview deployments for flashko-ibro
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https:\/\/flashko-ibro(-[a-zA-Z0-9_-]+)?\.vercel\.app$",
]

# Support optional env override to append more origins if needed
extra_cors_origins = os.getenv('CORS_ALLOWED_ORIGINS', '')
if extra_cors_origins:
    for o in extra_cors_origins.split(','):
        if o.strip() and o.strip() not in CORS_ALLOWED_ORIGINS:
            CORS_ALLOWED_ORIGINS.append(o.strip())

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
CSRF_TRUSTED_ORIGINS = [
    'https://flashko-ibro.vercel.app',
    'https://flashkobackend21.pythonanywhere.com',
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]
extra_csrf_origins = os.getenv('CSRF_TRUSTED_ORIGINS', '')
if extra_csrf_origins:
    for o in extra_csrf_origins.split(','):
        if o.strip() and o.strip() not in CSRF_TRUSTED_ORIGINS:
            CSRF_TRUSTED_ORIGINS.append(o.strip())


# Internationalization
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
