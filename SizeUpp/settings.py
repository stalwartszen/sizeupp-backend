import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
from django.contrib.messages import constants as messages


MESSAGE_TAGS = {
        messages.DEBUG: 'alert-secondary',
        messages.INFO: 'alert-info',
        messages.SUCCESS: 'alert-success',
        messages.WARNING: 'alert-warning',
        messages.ERROR: 'alert-danger',
 }

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-a-o+(dp£3=2sc!o9o#!y£j3)+c^9z+rz!2pqb£%w05nme=t*=^'
DEBUG = True
ALLOWED_HOSTS = ['*','https://traxzen.pythonanywhere.com']


INSTALLED_APPS = [
    # 'material',
    #  'material.admin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'authentication',
    'product',
    'dashboard',
    'ckeditor',
    'crispy_forms',
    'taggit',
    'rest_framework.authtoken',
    "corsheaders",
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'drf_yasg',

]
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
}
SITE_ID = 1
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': 'your-client-id',
            'secret': 'your-client-secret',
            'key': '',
        }
    }
}
CORS_ALLOW_METHODS = (
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
)
CORS_ALLOWED_ORIGINS = [
    "http://*",  # Also, add the scheme for consistency
    # Add other allowed origins as needed with the correct scheme
]
CORS_ALLOW_ALL_ORIGINS = True  # Set this to False to use CORS_ALLOWED_ORIGINS

CORS_ALLOW_HEADERS = (
    "accept",
    "authorization",
    "content-type",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
     'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
        'allauth.account.middleware.AccountMiddleware',

    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'SizeUpp.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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


WSGI_APPLICATION = 'SizeUpp.wsgi.application'

user = os.environ.get('USER')

DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
        }


DATA_UPLOAD_MAX_MEMORY_SIZE = 52428800  # 50 megabytes



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


LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Media files
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

#static files
STATIC_URL = '/static/'
# STATICFILES_DIRS = [BASE_DIR ,"staticfiles",]
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'staticfiles')]



DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = "authentication.User"

LOGOUT_REDIRECT_URL = "/"  # new
