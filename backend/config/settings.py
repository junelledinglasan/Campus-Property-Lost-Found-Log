"""Settings ng Lost & Found Log backend.

Sa development, walang kailangang i-set: may mga default na.
Sa production, i-set ang mga environment variable sa .env.example.
"""
import os
from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured

from lostfound.s3options import supabase_s3_options

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
    'whitenoise.middleware.WhiteNoiseMiddleware',
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

# Database: SQLite sa laptop (walang kailangang i-set). Kapag may DATABASE_URL, iyon ang gagamitin,
# hal. ang PostgreSQL ng Supabase: postgresql://user:password@host:5432/postgres?sslmode=require
DATABASE_URL = os.environ.get('DATABASE_URL', '').strip()
if DATABASE_URL:
    DATABASES = {'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600, conn_health_checks=True)}
else:
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

# Ang na-build na frontend (frontend/dist) ay kinokopya dito ng build.sh, at ang Django ang nagse-serve.
FRONTEND_DIST = BASE_DIR / 'frontend_dist'
if (FRONTEND_DIST / 'index.html').exists():
    WHITENOISE_ROOT = FRONTEND_DIST
    WHITENOISE_INDEX_FILE = True
WHITENOISE_MIMETYPES = {'.webmanifest': 'application/manifest+json'}

# Public na larawan ng found items.
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
# Pribado ang handover photos: wala sa MEDIA_ROOT, kaya hindi mabubuksan sa pamamagitan ng URL.
PRIVATE_MEDIA_ROOT = BASE_DIR / 'private_media'

# Supabase Storage (S3-compatible) para sa mga larawan. Kapag walang SUPABASE_S3_ACCESS_KEY,
# sa disk (MEDIA_ROOT at PRIVATE_MEDIA_ROOT) mase-save ang mga larawan gaya ng dati.
SUPABASE_PROJECT_REF = os.environ.get('SUPABASE_PROJECT_REF', '').strip()
SUPABASE_S3_ACCESS_KEY = os.environ.get('SUPABASE_S3_ACCESS_KEY', '').strip()
SUPABASE_S3_SECRET_KEY = os.environ.get('SUPABASE_S3_SECRET_KEY', '').strip()
SUPABASE_S3_REGION = os.environ.get('SUPABASE_S3_REGION', '').strip()
SUPABASE_BUCKET_ITEMS = os.environ.get('SUPABASE_BUCKET_ITEMS', 'lf-items').strip()
SUPABASE_BUCKET_HANDOVER = os.environ.get('SUPABASE_BUCKET_HANDOVER', 'lf-handover').strip()
USE_SUPABASE_STORAGE = bool(SUPABASE_S3_ACCESS_KEY and SUPABASE_S3_SECRET_KEY)

if USE_SUPABASE_STORAGE and not (SUPABASE_PROJECT_REF and SUPABASE_S3_REGION):
    raise ImproperlyConfigured('Kailangan ang SUPABASE_PROJECT_REF at SUPABASE_S3_REGION kasama ng S3 keys.')


STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage' if DEBUG
        else 'whitenoise.storage.CompressedStaticFilesStorage',
    },
}
if USE_SUPABASE_STORAGE:
    # Public bucket ang para sa items: diretso sa Supabase ang URL ng larawan.
    STORAGES['default'] = {
        'BACKEND': 'storages.backends.s3.S3Storage',
        'OPTIONS': {
            **supabase_s3_options(SUPABASE_BUCKET_ITEMS, SUPABASE_PROJECT_REF, SUPABASE_S3_ACCESS_KEY, SUPABASE_S3_SECRET_KEY, SUPABASE_S3_REGION),
            'querystring_auth': False,
            'custom_domain': f'{SUPABASE_PROJECT_REF}.supabase.co/storage/v1/object/public/{SUPABASE_BUCKET_ITEMS}',
        },
    }

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
    # Bilang ng proxy sa harap ng app (1 sa Render), para tamang IP ng bisita ang binibilang ng throttle.
    'NUM_PROXIES': int(os.environ['DRF_NUM_PROXIES']) if os.environ.get('DRF_NUM_PROXIES') else None,
}

CORS_ALLOWED_ORIGINS = env_list('CORS_ALLOWED_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173')
CSRF_TRUSTED_ORIGINS = env_list('CSRF_TRUSTED_ORIGINS', '')

if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    # Nasa likod ng proxy ng host (HTTPS ang tinatapos nila), kaya ito ang pinagbabasehan ng Django.
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
