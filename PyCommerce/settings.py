"""
Django settings for PyCommerce project.
"""

from pathlib import Path

import dj_database_url
from decouple import Csv, config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())


INSTALLED_APPS = [
    # django-unfold must come before django.contrib.admin
    'unfold',
    'unfold.contrib.filters',
    'unfold.contrib.forms',
    'unfold.contrib.inlines',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # Third-party
    'allauth',
    'allauth.account',
    'crispy_forms',
    'crispy_tailwind',

    # Local apps
    'store',
    'cart',
    'accounts',
]

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'PyCommerce.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'cart.context_processors.cart',
                'store.context_processors.categories',
                'store.context_processors.site_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'PyCommerce.wsgi.application'


# Database — Neon.tech Postgres via DATABASE_URL
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL'),
        conn_max_age=600,
        ssl_require=True,
    ),
}


AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]


LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Static & media
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'},
}

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Crispy Forms (Tailwind)
CRISPY_ALLOWED_TEMPLATE_PACKS = 'tailwind'
CRISPY_TEMPLATE_PACK = 'tailwind'


# Allauth
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
ACCOUNT_LOGIN_METHODS = {'email', 'username'}
ACCOUNT_SIGNUP_FIELDS = ['username*', 'email*', 'password1*', 'password2*']
ACCOUNT_EMAIL_VERIFICATION = 'none'


# Cart session key
CART_SESSION_ID = 'cart'


# Email (dev: write to console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# django-unfold admin theme
UNFOLD = {
    'SITE_TITLE': 'PyCommerce Admin',
    'SITE_HEADER': 'PyCommerce',
    'SITE_SUBHEADER': 'Store administration',
    'SITE_URL': '/',
    'SITE_SYMBOL': 'shopping_cart',
    'SHOW_HISTORY': True,
    'SHOW_VIEW_ON_SITE': True,
    'SHOW_BACK_BUTTON': True,
    'THEME': None,  # let user toggle light/dark
    'BORDER_RADIUS': '8px',
    'COLORS': {
        'primary': {
            '50': '238 242 255',
            '100': '224 231 255',
            '200': '199 210 254',
            '300': '165 180 252',
            '400': '129 140 248',
            '500': '99 102 241',
            '600': '79 70 229',
            '700': '67 56 202',
            '800': '55 48 163',
            '900': '49 46 129',
            '950': '30 27 75',
        },
    },
    'SIDEBAR': {
        'show_search': True,
        'show_all_applications': True,
        'navigation': [
            {
                'title': 'Storefront',
                'separator': True,
                'items': [
                    {
                        'title': 'Site settings',
                        'icon': 'tune',
                        'link': '/admin/store/sitesettings/',
                    },
                    {
                        'title': 'Hero sections',
                        'icon': 'view_carousel',
                        'link': '/admin/store/hero/',
                    },
                ],
            },
            {
                'title': 'Catalog',
                'separator': True,
                'items': [
                    {
                        'title': 'Products',
                        'icon': 'inventory_2',
                        'link': '/admin/store/product/',
                    },
                    {
                        'title': 'Categories',
                        'icon': 'category',
                        'link': '/admin/store/category/',
                    },
                    {
                        'title': 'Coupons',
                        'icon': 'local_offer',
                        'link': '/admin/store/coupon/',
                    },
                    {
                        'title': 'Product sections',
                        'icon': 'view_agenda',
                        'link': '/admin/store/productsection/',
                    },
                ],
            },
            {
                'title': 'Sales',
                'separator': True,
                'items': [
                    {
                        'title': 'Orders',
                        'icon': 'receipt_long',
                        'link': '/admin/store/order/',
                    },
                ],
            },
            {
                'title': 'Communication',
                'separator': True,
                'items': [
                    {
                        'title': 'Messages',
                        'icon': 'mail',
                        'link': '/admin/store/contactmessage/',
                    },
                ],
            },
            {
                'title': 'Users',
                'separator': True,
                'items': [
                    {
                        'title': 'Users',
                        'icon': 'person',
                        'link': '/admin/auth/user/',
                    },
                    {
                        'title': 'Groups',
                        'icon': 'group',
                        'link': '/admin/auth/group/',
                    },
                ],
            },
        ],
    },
}
