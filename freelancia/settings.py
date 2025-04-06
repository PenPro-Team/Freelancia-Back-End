"""
Django settings for freelancia project.

Generated by 'django-admin startproject' using Django 5.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from datetime import timedelta
from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-t#)8(0vj!36x(w*gi^+%7kmi9!d^srw_p%78400uq6cba-*^x@'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'channels',
    'rest_framework',
    'rest_framework_simplejwt',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'freelancia_back_end',
    'reviews',
    'django_filters',
    'contract',
    'corsheaders',
    'rest_framework_simplejwt.token_blacklist',
    'portfolio',
    'payments',
    'rest_framework.authtoken',
    'chat',
    'chatbot'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]


CORS_ALLOW_ALL_ORIGINS = True


ROOT_URLCONF = 'freelancia.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  # added by mustafa for email templates
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

WSGI_APPLICATION = 'freelancia.wsgi.application'
ASGI_APPLICATION = 'freelancia.asgi.application'

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

PAYPAL_CLIENT_ID = 'AWXLHM_HOQ6-DiakQ9MAvw7yCi_AOzfTuFjFmbHPVAOMVoZf7s9h8ExKTeqhIKzU0elb4KY7lzuvhpW5'
PAYPAL_SECRET = 'EAFWBvxhk6XRyGy5nQN-S72dhbMVhq4DjkWXc_Qfa3i0Uuk9jJvAKSwNp3g18zPvFMkVbBKV8fAW4bHJ'
PAYPAL_MODE = 'sandbox' 

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Chenging the default user to the Custom Created User
AUTH_USER_MODEL = 'freelancia_back_end.User'

# Media Path
MEDIA_URL = '/attachments/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'attachments')
# Temp Uploaded Folder (Till Saving The FILES)
FILE_UPLOAD_TEMP_DIR = os.path.join(BASE_DIR, 'tmp')

# AUTHENTICATION For Login
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'freelancia_back_end.permissions.IsOwnerOrAdminOrReadOnly',
    ],
}

SIMPLE_JWT = {
    'REFRESH_TOKEN_LIFETIME': timedelta(days=15),
    'ACCESS_TOKEN_LIFETIME': timedelta(days=15),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.privateemail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'freelancia-team@freelancia.site'
EMAIL_HOST_PASSWORD = 'PenPro55555'
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'freelancia-team@freelancia.site'

"""
# Channels work in Memmory , Use it for test (windows if the redis not Dockerize)
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}
"""
"""
Notes by Abd-Allah Abo-ElMagd:
    Redis Server will be used for Channels , 
    Need to Docerize Redis before deploy , 
    Will Not Work in Windows without Docker
    In linux install redis firs
        sudo apt-get install redis
    expiry value in seconds , it will delete the messages from hard after 1 hour if its value is 3600
    hosts takes the redis-server host and port
"""

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
            "expiry": 3600,
        },
    },
}



# # Celery Configuration for chatbot



# # --- Celery Configuration ---
# CELERY_BROKER_URL = 'redis://localhost:6379/0'
# CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
# CELERY_ACCEPT_CONTENT = ['json']
# CELERY_TASK_SERIALIZER = 'json'
# CELERY_RESULT_SERIALIZER = 'json'
# CELERY_TIMEZONE = 'Africa/Cairo'

# CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
# CELERY_BEAT_SCHEDULE = {
#     'update-faiss-index-every-hour': { # اسم وصفي للمهمة المجدولة
#         'task': 'chatbot.tasks.update_faiss_index_task', # المسار الكامل لدالة المهمة (سننشئها لاحقًا)
#         'schedule': 3600.0, # كل ساعة (3600 ثانية)
#     },
# }