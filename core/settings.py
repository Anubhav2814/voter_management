"""
Django settings for core project.
Generated for BrainstormerAI on 2025-04-22 06:09:12
"""

from pathlib import Path
import os
from datetime import datetime
import tempfile
from decouple import config, Csv
from django.contrib.messages import constants as messages


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
SECRET_KEY = config('98765216539821JKHFbnbavsnvd&^(*&^(*%', default='django-insecure-your-secret-key-here')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='*', cast=Csv())

CSRF_TRUSTED_ORIGINS = ['http://localhost:8000', 'http://127.0.0.1:8000']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'notifications.apps.NotificationsConfig',
    'voters.apps.VotersConfig',
    'rangefilter',
    'rest_framework',
    'widget_tweaks',
    'passes',
    'ckeditor',
    'ckeditor_uploader',
    'news',
    'rest_framework.authtoken',
    'blogs',
    'Media_Management',
    'events',
    'invitations',
]



CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'height': 300,
        'width': '100%',
        'toolbar_full': [
            ['Styles', 'Format', 'Bold', 'Italic', 'Underline', 'Strike', 'SpellChecker', 'Undo', 'Redo'],
            ['Link', 'Unlink', 'Anchor'],
            ['Image', 'Flash', 'Table', 'HorizontalRule'],
            ['TextColor', 'BGColor'],
            ['Smiley', 'SpecialChar'],
            ['Source'],
            ['JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            ['NumberedList', 'BulletedList'],
            ['Indent', 'Outdent'],
            ['Maximize'],
        ],
        'extraPlugins': ','.join([
            'uploadimage',  # the upload image feature
            'autolink',
            'autoembed',
            'embedsemantic',
            'autogrow',
            'widget',
            'lineutils',
            'clipboard',
            'dialog',
            'dialogui',
            'elementspath'
        ]),
    }
}

# Required CKEditor settings
CKEDITOR_UPLOAD_PATH = 'uploads/'
CKEDITOR_IMAGE_BACKEND = 'pillow'
CKEDITOR_JQUERY_URL = '//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js'
CKEDITOR_BROWSE_SHOW_DIRS = True

# Static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# REST Framework Settings
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        # 'rest_framework.authentication.SessionAuthentication',
        # 'rest_framework.authentication.BasicAuthentication',
        # 'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50
}



MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'core', 'templates'),
            os.path.join(BASE_DIR, 'templates'),
            os.path.join(BASE_DIR, 'voters', 'templates'),
            os.path.join(BASE_DIR, 'notifications', 'templates'),
            os.path.join(BASE_DIR, 'passes', 'templates'),
            os.path.join(BASE_DIR, 'blogs', 'templates'),
            os.path.join(BASE_DIR, 'Media_Management', 'templates'),
            os.path.join(BASE_DIR, 'news', 'templates'),
            os.path.join(BASE_DIR, 'events', 'templates'),
            os.path.join(BASE_DIR, 'invitations', 'templates'),

        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.settings.global_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# Database Configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME', default='voter_management'),
        'USER': config('DB_USER', default='voter_admin'),
        'PASSWORD': config('DB_PASSWORD', default='voter123'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='3306'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
        },
        'TEST': {
            'NAME': 'test_voter_management',
            'CHARSET': 'utf8',
            'COLLATION': 'utf8_general_ci',
        },
    }
}



# Password validation
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
LANGUAGE_CODE = config('LANGUAGE_CODE', default='en-us')
TIME_ZONE = config('TIME_ZONE', default='UTC')
USE_I18N = True
USE_TZ = True

# Static and Media Files Configuration
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# # CKEditor configuration
# CKEDITOR_CONFIGS = {
#     'default': {
#         'toolbar': 'full',
#         'height': 300,
#         'width': '100%',
#     },
# }



# Create necessary directories
for directory in [STATIC_ROOT, MEDIA_ROOT, os.path.join(BASE_DIR, 'static')]:
    os.makedirs(directory, exist_ok=True)

# WeasyPrint Configuration for PDF Generation
WEASYPRINT_FONT_CONFIG = {
    'pdf-configuration': {
        'font-family': 'Arial, sans-serif',
    }
}

# Temporary Directory Configuration
TEMP_DIR = tempfile.gettempdir()
if not os.access(TEMP_DIR, os.W_OK):
    TEMP_DIR = os.path.join(BASE_DIR, 'temp_files')
    os.makedirs(TEMP_DIR, mode=0o777, exist_ok=True)

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'captainsparrow2814@gmail.com'
EMAIL_HOST_PASSWORD = 'ukrj hhjm otht wxxu'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
EMAIL_TIMEOUT = 60  # Increased timeout
SERVER_EMAIL = 'captainsparrow2814@gmail.com'

# Add these for additional security
EMAIL_USE_SSL = False
EMAIL_SSL_CERTFILE = None
EMAIL_SSL_KEYFILE = None

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {module} {process:d} {thread:d} {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'debug.log'),
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        '': {  # Root logger
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
        },
        'passes': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Admin Site Configuration
ADMIN_SITE_HEADER = "Voter Management System"
ADMIN_SITE_TITLE = "Voter Management System"
ADMIN_INDEX_TITLE = "Welcome to Voter Management System"

# Session Configuration
SESSION_COOKIE_AGE = config('SESSION_COOKIE_AGE', default=86400, cast=int)
SESSION_SAVE_EVERY_REQUEST = True

# SMS API Configuration
EDUMARC_API_KEY = 'clnnab4k2000bj7qx6h14fu7r'
EDUMARC_API_URL = 'https://smsapi.edumarcsms.com/api/v1/sendsms'
EDUMARC_SENDER_ID = 'EDUMRC'

# Voter Management Custom Settings
VOTER_EXCEL_UPLOAD_PATH = os.path.join(MEDIA_ROOT, 'excel_uploads')
VOTER_EXPORT_PATH = os.path.join(MEDIA_ROOT, 'exports')
os.makedirs(VOTER_EXCEL_UPLOAD_PATH, exist_ok=True)
os.makedirs(VOTER_EXPORT_PATH, exist_ok=True)

# Current User and Timestamp
CURRENT_USER = 'BrainstormerAI'
CURRENT_TIMESTAMP = '2025-04-22 06:09:12'

# Cache Settings
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Custom Template Context Processor
def global_settings(request):
    return {
        'ADMIN_SITE_HEADER': ADMIN_SITE_HEADER,
        'CURRENT_USER': CURRENT_USER,
        'CURRENT_TIMESTAMP': CURRENT_TIMESTAMP,
    }

MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

# Make messages persist even after redirect
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

# # Admin Site Customization
# ADMIN_SITE_HEADER = "News Management System"
# ADMIN_SITE_TITLE = "News Management"
# ADMIN_INDEX_TITLE = "News Management Administration"
#
# # Update admin site configurations
# from django.contrib import admin
# admin.site.site_header = ADMIN_SITE_HEADER
# admin.site.site_title = ADMIN_SITE_TITLE
# admin.site.index_title = ADMIN_INDEX_TITLE