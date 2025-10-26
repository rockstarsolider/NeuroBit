"""Django 5.2.4"""

import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv
from django.urls import reverse_lazy
from django.templatetags.static import static
from django.utils.translation import gettext_lazy as _

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = os.environ.get('DEBUG') == 'True' or os.environ.get('DEBUG') == 'true'
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1,0.0.0.0").split(",")

# Application definition
INSTALLED_APPS = [
    "unfold",  # before django.contrib.admin
    "unfold.contrib.filters",  # optional, if special filters are needed
    "unfold.contrib.forms",  # optional, if special form elements are needed
    "unfold.contrib.inlines",  # optional, if special inlines are needed
    "unfold.contrib.import_export",
    "unfold.contrib.simple_history",

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "django.contrib.humanize",

    "import_export",
    "simple_history",
    "crispy_forms",
    'webpack_loader',
    "django_extensions",
    'rosetta',

    "core.apps.CoreConfig",
    'pages',
    'courses',
]


# whitenoise
WHITENOISE_MAX_AGE = 60 * 60 * 24 * 180  # 180 days
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    }
}

# webpack-loader
WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': 'webpack_output/',
        'CACHE': not DEBUG,
        'STATS_FILE': os.path.join(BASE_DIR, 'webpack-stats.json'),
        'POLL_INTERVAL': 0.1,
        'IGNORE': [r'.+\.hot-update.js', r'.+\.map'],
    }
}


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",  # static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    "simple_history.middleware.HistoryRequestMiddleware",
]


ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'


# Database
DATABASES = {'default': dj_database_url.config(default=os.environ.get('DATABASE_URL'))}


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

# LANGUAGE_CODE = 'fa-ir'
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Tehran'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Define the languages your site supports
LANGUAGES = (
    ('en', 'English'),
    ('fa', 'Farsi'),
)

# Path to store translation files (.po, .mo)
LOCALE_PATHS = (
    BASE_DIR / 'locale',
)

ROSETTA_REQUIRES_AUTH = True
ROSETTA_ACCESS_CONTROL_FUNCTION = 'core.utility.can_access_rosetta'

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
    os.path.join(BASE_DIR, 'static/webpack_output')
    ]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CRISPY_TEMPLATE_PACK = "unfold_crispy"
CRISPY_ALLOWED_TEMPLATE_PACKS = ["unfold_crispy"]
# unfold
UNFOLD = {
    # "TABS": "config.admin.tabs_callback",
    # "SHOW_LANGUAGES": True,
    "STYLES": ["css/admin-fixes.css"],
    "SITE_DROPDOWN": [
        {
            "icon": "home",
            "title": _("Home"),
            "link": reverse_lazy("admin:index"),
        },
        {
            "icon": "info",
            "title": _("about us"),
            "link": reverse_lazy("home"),
        },
    ],
    "SITE_TITLE": "Neurobit",
    "SITE_HEADER": "Admin Panel",
    "SITE_SUBHEADER": "Neurobit",
    "SITE_SYMBOL": "settings",
    "LOGIN": {
        "image": lambda request: static(r"images/neurobit_main_logo.webp"),
        # "redirect_after": lambda request: reverse_lazy("admin:APP_MODEL_changelist"),
    },
    "SIDEBAR": {
        "show_search": True, 
        "show_all_applications": True, 
        "navigation": [
            {
                "title": _("Navigation"),
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": _("Dashboard"),
                        "icon": "dashboard",  # Supported icon set: https://fonts.google.com/icons
                        "link": reverse_lazy("admin:index"),
                    },
                    {
                        "title": _("Users"),
                        "icon": "people",
                        "link": reverse_lazy("admin:core_customuser_changelist"),
                    },
                    {
                        "title": _("Mentors"),
                        "icon": "support_agent",
                        "link": reverse_lazy("admin:courses_mentor_changelist"),
                    },
                    {
                        "title": _("Learners"),
                        "icon": "child_care",
                        "link": reverse_lazy("admin:courses_learner_changelist"),
                    },
                    {
                        "title": _("Subscriptions Analytics"),
                        "icon": "query_stats",
                        "link": reverse_lazy("admin:courses_learnersubscribeplan_analytics"), 
                    },
                    # {
                    #     "title": _("Subscriptions PDF"),
                    #     "icon": "picture_as_pdf",
                    #     "link": reverse_lazy("admin:courses_learnersubscribeplan_export_pdf"),
                    # },
                    {
                        "title": _("SMS Notifications"),
                        "icon": "sms",
                        "link": reverse_lazy("admin:core_subscriptionnotificationconfig_changelist"),
                    },

                ],
            },
            {
                "title": _("Courses"),
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": _("Courses"),
                        "icon": "school",
                        "link": reverse_lazy("admin:app_list", kwargs={'app_label': 'courses'}),
                    },
                    {
                        "title": _("LearnerSubscribePlan"),
                        "icon": "currency_exchange",
                        "link": reverse_lazy("admin:courses_learnersubscribeplan_changelist"),
                    },
                    {
                        "title": _("Mentor Assignment"),
                        "icon": "group_add",
                        "link": reverse_lazy("admin:courses_mentorassignment_changelist"),
                    },
                    {
                        "title": _("Educational Steps"),
                        "icon": "format_list_numbered",
                        "link": reverse_lazy("admin:courses_educationalstep_changelist"),
                    },
                    {
                        "title": _("Task Evaluation"),
                        "icon": "verified",
                        "link": reverse_lazy("admin:courses_taskevaluation_changelist"),
                    },
                    {
                        "title": _("Social Post"),
                        "icon": "article_person",
                        "link": reverse_lazy("admin:courses_socialpost_changelist"),
                    },
                    {
                        "title": _("MentorGroupSessionParticipant"),
                        "icon": "adaptive_audio_mic",
                        "link": reverse_lazy("admin:courses_mentorgroupsessionparticipant_changelist"),
                    },
                ]
            },
            {
                "title": _("Applications"),
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": _("Applications"),
                        "icon": "upload",
                        "link": reverse_lazy("admin:app_list", kwargs={'app_label': 'pages'}),
                    },
                ]
            },
        ],
    },
}

AUTH_USER_MODEL = 'core.CustomUser'

# --- django-import-export ---
IMPORT_EXPORT_USE_TRANSACTIONS = True

# Optional: toggle WeasyPrint on/off (dev default: off on Windows)
USE_WEASYPRINT = os.getenv("USE_WEASYPRINT") == "true"
# Optional: hide PDF unless WeasyPrint is usable (you already have USE_WEASYPRINT)
if USE_WEASYPRINT:
    IMPORT_EXPORT_ENABLE_PDF = True
else:
    IMPORT_EXPORT_ENABLE_PDF = False

print("DEBUG", DEBUG)
# debug-toolbar
if DEBUG:
    INSTALLED_APPS += ["debug_toolbar",]
    MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware",]
    INTERNAL_IPS = ["127.0.0.1", "localhost", "::1"]
    # Show toolbar on every DEBUG request
    DEBUG_TOOLBAR_CONFIG = {"SHOW_TOOLBAR_CALLBACK": lambda request: True}