import os
from decouple import config
from .ckeditor_config import *

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = '-j5h#qd*=^!*#7p+(@*^jo80f6vzpb2(l7vmf&hv_6&2hwg5fn'

ALLOWED_HOSTS = ['*']


# INTERNAL_IPS = [
#     # ...
#     '127.0.0.1',
#     # ...
# ]

DEBUG = config('DEBUG', default=True, cast=bool)
LIVE = config('LIVE', default=True, cast=bool)

INSTALLED_APPS = [

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sites',
    'schedulejob.apps.SchedulejobConfig',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',

    'rest_framework',
    'rest_framework_swagger',
    'corsheaders',
    'mptt',
    'anymail',
    'ckeditor',
    'ckeditor_uploader',
    'django_extensions',

    # 'easy_select2',
    'imagekit',

    'accounts',
    # 'catalog.apps.CatalogConfig',
    'catalog',
    'sales',
    'settings',
    'dashboard',
    'client',
    'marketing',
    'payment',
    'utility',
    'NewsletterandContact',
    'store',
    'landing',
    'vendorAnddelivery',

    'smarttech_payment_api',

    #debug toolbar
    # 'debug_toolbar',

    'django_filters',
    'crispy_forms',

]

CRISPY_TEMPLATE_PACK = 'bootstrap4'


import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="https://d8b449824c434bc484fc40f5793b2f4d@o485539.ingest.sentry.io/5541042",
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,

    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True
)
GRAPH_MODELS = {
  'all_applications': True,
  'group_models': True,
}

MIDDLEWARE = [

    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# ckeditor config
CKEDITOR_JQUERY_URL = 'https://ajax.googleapis.com/ajax/libs/jquery/2.2.4/jquery.min.js'
CKEDITOR_UPLOAD_PATH = 'uploads/'
CKEDITOR_IMAGE_BACKEND = "pillow"
CKEDITOR_BROWSE_SHOW_DIRS = True
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline'],
            ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'JustifyLeft', 'JustifyCenter',
             'JustifyRight', 'JustifyBlock'],
            ['Link', 'Unlink'],
            ['RemoveFormat', 'Source']
        ],
        'height': 200,
        'width': '100%',
    }
}

ROOT_URLCONF = 'ordersathi.urls'
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR, ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'client.processors.cart_count',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                # `allauth` needs this from django
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'ordersathi.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config('DATABASE_NAME'),
        'USER': 'postgres',
        'PASSWORD': config('DATABASE_PASSWORD'),
        'HOST': config('DATABASE_HOST'),
        'PORT': config('DATABASE_PORT'),

    },
}

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

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

# overriding allauth forms
ACCOUNT_FORMS = {
    'signup': 'accounts.forms.CustomSignupForm',
    'login': 'accounts.forms.CustomLoginForm',
    'change_password': 'accounts.forms.CustomChangePasswordForm',
    'reset_password': 'accounts.forms.CustomPasswordResetForm',
    'reset_password_from_key': 'accounts.forms.CustomPasswordResetFromKeyForm',
    'set_password': 'accounts.forms.CustomPasswordSetForm',
}

# CORS_ORIGIN_WHITELIST = (
# # 'http://localhost:3001',
# 'http://localhost:3000',
# 'http://localhost:8000',
# )
CORS_ORIGIN_ALLOW_ALL = True


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

TIME_INPUT_FORMATS = ['%H:%M',]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'ordersathi/static')
]

AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',
    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
)

SITE_ID = 5

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'in-v3.mailjet.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = 'ce2617c0813a662a6e9eb25f969dcd22'
EMAIL_HOST_PASSWORD = 'a69e3b2d1f092a6ffbdc2366dcf11a8a'

ANYMAIL = {
    "MAILJET_API_KEY": "ce2617c0813a662a6e9eb25f969dcd22",
    "MAILJET_SECRET_KEY": "a69e3b2d1f092a6ffbdc2366dcf11a8a",
}
# EMAIL_BACKEND = "anymail.backends.mailjet.EmailBackend"
DEFAULT_FROM_EMAIL = 'info@ordersathi.com'

ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = '/'
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = 'username'
ACCOUNT_USERNAME_REQUIRED = False
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/login/'
SESSION_SAVE_EVERY_REQUEST = True

'''Nep express resturant'''
DELIVERY_API_USERNAME = "demo"
DELIVERY_API_PASSWORD = "demo12345"
DELIVERY_API_EMAIL = "demoapi@gmail.com"

LOGOUT_REDIRECT_URL = "/admin"

'''for fb login'''
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"
DEFAULT_HTTP_PROTOCOL = "https"

# REST_FRAMEWORK = {
#     'DEFAULT_PARSER_CLASSES': [
#         'rest_framework.parsers.JSONParser',
#     ]
# }

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    )
}
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'apps.core.pagination.StandardResultsSetPagination'
}

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    # 'PAGE_SIZE': 2
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    # 'DEFAULT_PARSER_CLASSES': [
    #     'rest_framework.parsers.JSONParser',
    # ],
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend']
}

# REST_FRAMEWORK = {
#     'DEFAULT_PARSER_CLASSES': [
#         'rest_framework.parsers.JSONParser',
#     ]
# }


from datetime import timedelta
from django.conf import settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),#specifies how long access tokens are valid
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),#specifies how long refresh tokens are valid
    'ROTATE_REFRESH_TOKENS': False,#When set to True, if a refresh token is submitted to the TokenRefreshView, a new refresh token will be returned along with the new access token
    'BLACKLIST_AFTER_ROTATION': True,#When set to True, causes refresh tokens submitted to the TokenRefreshView to be added to the blacklist if the blacklist app is in use and the ROTATE_REFRESH_TOKENS setting is set to True

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': settings.SECRET_KEY,
    'VERIFYING_KEY': None,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=60),#specifies how long sliding tokens are valid to prove authentication after token generation.
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),#specifies how long sliding tokens are valid to be refreshed
}



# print(NICA_PG_ACCESS_KEY,"--")
# print(NICA_PG_PROFILE_ID,"--")
# print(NICA_PG_SECRET_KEY,"--")
# print(NICA_PG_URL,"--")



# DEBUG_TOOLBAR_PANELS = [
#     'debug_toolbar.panels.history.HistoryPanel',
#     'debug_toolbar.panels.versions.VersionsPanel',
#     'debug_toolbar.panels.timer.TimerPanel',
#     'debug_toolbar.panels.settings.SettingsPanel',
#     'debug_toolbar.panels.headers.HeadersPanel',
#     'debug_toolbar.panels.request.RequestPanel',
#     'debug_toolbar.panels.sql.SQLPanel',
#     'debug_toolbar.panels.staticfiles.StaticFilesPanel',
#     'debug_toolbar.panels.templates.TemplatesPanel',
#     'debug_toolbar.panels.cache.CachePanel',
#     'debug_toolbar.panels.signals.SignalsPanel',
#     'debug_toolbar.panels.logging.LoggingPanel',
#     'debug_toolbar.panels.redirects.RedirectsPanel',
#     'debug_toolbar.panels.profiling.ProfilingPanel',
# ]

SWAGGER_SETTINGS = {
'LOGIN_URL': 'rest_framework:login',
'LOGOUT_URL': 'rest_framework:logout',
}






# SOCIALACCOUNT_ADAPTER = 'accounts.adaptors.MyAdapter'

if  not DEBUG:
    #securities in production
    CSRF_COOKIE_SECURE = True #to avoid transmitting the CSRF cookie over HTTP accidentally.
    SESSION_COOKIE_SECURE = True #to avoid transmitting the session cookie over HTTP accidentally.

    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True  
    # SECURE_SSL_REDIRECT = True # redirect all non-HTTPS requests to HTTPS.

    X_FRAME_OPTIONS='DENY'
