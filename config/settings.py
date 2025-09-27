from pathlib import Path
import os
import dj_database_url # <--- REQUIRED FOR HEROKU POSTGRES

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
SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-caf&m(t%s3i4xfltn8tq&ahxm1+w#p_i0!^^4czuszk@4=h8p)")

# Heroku sets DEBUG to False automatically unless overridden.
DEBUG = os.environ.get("DEBUG", "False") == "True"

# REQUIRED for Heroku deployment
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

# Only needed for local development tools (can be removed for production)
NPM_BIN_PATH = "C:/Program Files/nodejs/npm.cmd" 
TAILWIND_APP_NAME = 'theme' 

# --- APPLICATION DEFINITION ---

INSTALLED_APPS = [
    # Required for S3 integration
    'storages', # <--- ADD THIS
    
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

# --- S3/STATIC/MEDIA CONFIGURATION ---

# 1. AWS Credentials (Pull from Heroku Config Vars)
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'ap-southeast-1') 

# 2. General S3 Settings (These ensure public access which is needed for static files)
AWS_DEFAULT_ACL = 'public-read' 
AWS_QUERYSTRING_AUTH = False 
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com'

# 3. STATIC FILES (Django looks here)
STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'

# IMPORTANT: You must keep STATIC_ROOT for collectstatic to function on Heroku.
# This points to a temporary folder during the build process.
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') 

# This line is often redundant when using S3 and can cause the Heroku warning, 
# but we keep it minimal in case you have files outside of 'theme/static'.
# If you only have files in 'theme/static', you can remove this entirely.
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'theme/static'),
]

# 4. MEDIA FILES (For user uploads, if any)
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'


# --- DEFAULT AND I18N ---

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Password validation and other non-critical sections were omitted for brevity
# but should remain in your final file.