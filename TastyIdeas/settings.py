from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-=+6@jacfy9_sk3b3x_=qd4mo1e$*a--v32me%$7bv#)x@*crlr'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'TastyIdeas.api',
    'TastyIdeas.accounts',
    'TastyIdeas.interactions',
    'TastyIdeas.recipe',

    'rest_framework',
    'rest_framework.authtoken',
    'djoser',
    'django_cleanup',
    'django_summernote',
    'widget_tweaks',
    'django_admin_logs',
    'django.contrib.humanize',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'TastyIdeas.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                'TastyIdeas.common.context_processors.current_url_name',

            ],
        },
    },
]

WSGI_APPLICATION = 'TastyIdeas.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'tasty_db',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432'
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Accounts

AUTHENTICATION_BACKENDS = [
    'TastyIdeas.accounts.auth.UserEmailOrUsernameAuth'
]

AUTH_USER_MODEL = 'accounts.User'

LOGIN_URL = '/accounts/login/'

LOGOUT_REDIRECT_URL = '/'

# Rest framework

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ]
}

DJOSER = {
    'EMAIL': {
        'password_reset': 'TastyIdeas.api.accounts.views.PasswordResetEmail'
    },

    'PASSWORD_RESET_CONFIRM_URL': 'accounts/reset/{uid}/{token}',
    'SERIALIZERS': {
        'user': 'TastyIdeas.api.accounts.serializers.UserSerializer',
        'current_user': 'TastyIdeas.api.accounts.serializers.UserSerializer',
    },
}

RECIPES_PAGINATE_BY = 10  # Display 10 recipes per page
EMAIL_SEND_INTERVAL_SECONDS = 300  # Send verification emails every 5 minutes
CATEGORIES_PAGINATE_BY = 20  # Display 20 categories per page
COMMENTS_PAGINATE_BY = 50  # Display 50 comments per page

DJANGO_ADMIN_LOGS_DELETABLE = True
DJANGO_ADMIN_LOGS_ENABLED = False


# Logging

FILE_HANDLER = {
    'class': 'logging.handlers.RotatingFileHandler',
    'maxBytes': 1024 * 1024 * 10,
    'backupCount': 10,
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'detailed': {
            'format': '[{asctime}] - {levelname} - {filename} on line {lineno}:\n{message}\n\n',
            'datefmt': "%Y/%b/%d %H:%M:%S",
            'style': '{',
        },

        'brief': {
            'format': '[{asctime}] - {levelname}:\n{message}',
            'datefmt': "%Y/%b/%d %H:%M:%S",
            'style': '{',
        },
    },

    'handlers': {
        'file_django': dict(
            FILE_HANDLER,
            formatter='detailed',
            filename=(BASE_DIR / 'logs/django.log'),
        ),

        'file_mailing': dict(
            FILE_HANDLER,
            formatter='brief',
            filename=(BASE_DIR / 'logs/mailing.log'),
            level='INFO',
        ),

        'file_accounts': dict(
            FILE_HANDLER,
            formatter='brief',
            filename=(BASE_DIR / 'logs/accounts.log'),
            level='INFO',
        ),
    },

    'loggers': {
        'django': {
            'handlers': ['file_django'],
            'level': 'WARNING',
        },

        "mailings": {
            "handlers": ["file_mailing"],
            "level": "INFO",
        },

        "accounts": {
            "handlers": ["file_accounts"],
            "level": "INFO",
        },
    },
}