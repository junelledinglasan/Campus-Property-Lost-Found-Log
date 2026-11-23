"""Settings ng Lost & Found Log backend.

Sa development, walang kailangang i-set: may mga default na.
Sa production, i-set ang mga environment variable sa .env.example.
"""
import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(name, default):
    return os.environ.get(name, str(default)).strip().lower() in ('1', 'true', 'yes', 'on')


def env_list(name, default=''):
    return [item.strip() for item in os.environ.get(name, default).split(',') if item.strip()]


DEBUG = env_bool('DJANGO_DEBUG', True)

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = 'dev-only-insecure-key-do-not-use-in-production'
    else:
        raise ImproperlyConfigured('I-set ang DJANGO_SECRET_KEY kapag naka-off ang DJANGO_DEBUG.')

ALLOWED_HOSTS = env_list('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'lostfound',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Manila'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Public na larawan ng found items.
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
# Pribado ang handover photos: wala sa MEDIA_ROOT, kaya hindi mabubuksan sa pamamagitan ng URL.
PRIVATE_MEDIA_ROOT = BASE_DIR / 'private_media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Ang mga larawan ay ipinapadala bilang base64 sa JSON, kaya mas malaki ang limit kaysa default.
DATA_UPLOAD_MAX_MEMORY_SIZE = 8 * 1024 * 1024

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ['lostfound.authentication.LenientTokenAuthentication'],
    # Ligtas bilang default: OSAS staff lang, maliban kung sinabing bukas sa lahat ang view.
    'DEFAULT_PERMISSION_CLASSES': ['lostfound.permissions.IsStaff'],
    'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer'],
    'EXCEPTION_HANDLER': 'lostfound.exceptions.api_exception_handler',
    'DEFAULT_THROTTLE_RATES': {
        'claim_submit': os.environ.get('THROTTLE_CLAIMS', '30/hour'),
        'login': os.environ.get('THROTTLE_LOGIN', '10/min'),
    },
}

CORS_ALLOWED_ORIGINS = env_list('CORS_ALLOWED_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173')
CSRF_TRUSTED_ORIGINS = env_list('CSRF_TRUSTED_ORIGINS', '')

if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
