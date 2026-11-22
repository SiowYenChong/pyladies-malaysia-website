from pathlib import Path
import os
import dj_database_url # <--- REQUIRED FOR HEROKU POSTGRES
from django.core.exceptions import ImproperlyConfigured

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- CORE SETTINGS ---
# Load environment variables from a .env file locally
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# SECRET_KEY and DEBUG should be pulled from environment variables in production
# SECRET_KEY must come from the environment (set it in App Service configuration)
SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise ImproperlyConfigured("The SECRET_KEY environment variable must be set.")

# Heroku sets DEBUG to False automatically unless overridden.
DEBUG = os.environ.get("DEBUG", "False") == "True"

# REQUIRED for Heroku deployment
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

# Azure App Service terminates HTTPS at the proxy, so trust its forwarded protocol
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
CSRF_TRUSTED_ORIGINS = [origin for origin in os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',') if origin]

# Only needed for local development tools (can be removed for production)
NPM_BIN_PATH = "C:/Program Files/nodejs/npm.cmd" 
TAILWIND_APP_NAME = 'theme' 

# --- APPLICATION DEFINITION ---

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    
    # other Django apps
    'tailwind',
    'theme'
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Configure django_browser_reload only if DEBUG is True
if DEBUG:
    INSTALLED_APPS += ['django_browser_reload']
    MIDDLEWARE += ["django_browser_reload.middleware.BrowserReloadMiddleware"]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / 'templates'],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# --- DATABASE CONFIGURATION ---
# Use SQLite locally, but switch to Heroku's PostgreSQL DATABASE_URL if available.
DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600
    )
}

# --- STATIC FILES (served by WhiteNoise, content lives in theme/static) ---
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'theme/static'),
]
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}


# --- DEFAULT AND I18N ---

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Password validation and other non-critical sections were omitted for brevity
# but should remain in your final file.