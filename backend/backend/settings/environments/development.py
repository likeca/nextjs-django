import logging.config
from ..env_vars import BASE_DIR
from ..base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TEMPLATES[0]["OPTIONS"].update({"debug": True})

STATIC_ROOT = BASE_DIR.joinpath("static")
MEDIA_ROOT = BASE_DIR.joinpath("media")

# Django Compressor for css and javascript - Not enable in development
# COMPRESS_OFFLINE = True
COMPRESS_ENABLED = True

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": lambda r: False,  # Disables debug_toolbar
}

# Django Debug Toolbar
INSTALLED_APPS += (
    "debug_toolbar",
    "django_browser_reload",
    # 'autotranslate',            # No need to deploy in production
)

# Additional middleware introduced by debug toolbar
MIDDLEWARE += (
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django_browser_reload.middleware.BrowserReloadMiddleware",
)
# Allow internal IPs for debugging
INTERNAL_IPS = [
    "127.0.0.1",
    "0.0.0.1",
]

# django-autotranslate change translation service
# AUTOTRANSLATE_TRANSLATOR_SERVICE = 'autotranslate.services.GoogleWebTranslatorService'
# AUTOTRANSLATE_TRANSLATOR_SERVICE = 'autotranslate.services.AzureAPITranslatorService'
# AZURE_TRANSLATOR_SECRET_KEY = env('AZURE_TRANSLATOR_SECRET_KEY')

# Disable browsable API render of django-rest-framework
# REST_FRAMEWORK = {
#     "DEFAULT_RENDERER_CLASSES": [
#         "rest_framework.renderers.JSONRenderer",
#     ],
# }

# Log everything to the logs directory at the top
LOGFILE_ROOT = BASE_DIR.joinpath("logs")

# Reset logging
# (see http://www.caktusgroup.com/blog/2015/01/27/Django-Logging-Configuration-logging_config-default-settings-logger/)
LOGGING_CONFIG = None
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[%(asctime)s] %(levelname)s [%(pathname)s:%(lineno)s] %(message)s",
            "datefmt": "%d/%b/%Y %H:%M:%S",
        },
        "simple": {
            "format": "%(levelname)s %(message)s",
        },
    },
    "handlers": {
        "django_log_file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": LOGFILE_ROOT.joinpath("django.log"),
            "encoding": "utf-8",
            "formatter": "verbose",
        },
        "proj_log_file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": LOGFILE_ROOT.joinpath("project.log"),
            "encoding": "utf-8",
            "formatter": "verbose",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    # In Development, log to console
    "loggers": {
        "django": {
            "handlers": ["django_log_file"],
            "propagate": True,
            "level": "DEBUG",
        },
        "project": {
            "handlers": ["console"],
            "level": "INFO",
        },
    },
}

logging.config.dictConfig(LOGGING)
