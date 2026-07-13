import logging.config
from ..env_vars import BASE_DIR
from ..base import *

# For security and performance reasons, DEBUG is turned off
# Must run "python manage.py collect static", otherwise cause Server Error (500)
DEBUG = False
TEMPLATE_DEBUG = False
# When DEBUG=False in Deployment. CSRF_TRUSTED_ORIGINS is already set from
# settings/rest.py (env.list with a sane default); only override if explicitly provided.
_csrf = env.list("CSRF_TRUSTED_ORIGINS", default=[])
if _csrf:
    CSRF_TRUSTED_ORIGINS = _csrf

STATIC_ROOT = BASE_DIR.joinpath("static")
MEDIA_ROOT = BASE_DIR.joinpath("media")

# Django Compressor for css and javascript
# COMPRESS_OFFLINE = True
COMPRESS_ENABLED = True

# Cache the templates in memory for speed-up
loaders = [
    (
        "django.template.loaders.cached.Loader",
        [
            "django.template.loaders.filesystem.Loader",
            "django.template.loaders.app_directories.Loader",
        ],
    ),
]

TEMPLATES[0]["OPTIONS"].update({"loaders": loaders})
TEMPLATES[0].update({"APP_DIRS": False})

# django-allauth For production only
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"

# Disable the browsable API renderer in production, but KEEP the auth /
# permission / pagination config defined in settings/rest.py.
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [
    "rest_framework.renderers.JSONRenderer",
]
# Log everything to the logs directory at the top
LOGFILE_ROOT = BASE_DIR.joinpath("logs")

# Reset logging
LOGGING_CONFIG = None
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[%(asctime)s] %(levelname)s [%(pathname)s:%(lineno)s] %(message)s",
            "datefmt": "%d/%b/%Y %H:%M:%S",
        },
        "simple": {"format": "%(levelname)s %(message)s"},
    },
    "handlers": {
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
            "formatter": "simple",
        },
    },
    # In production, log to file
    "loggers": {
        "project": {
            "handlers": ["proj_log_file"],
            "level": "DEBUG",
        }
    },
}

logging.config.dictConfig(LOGGING)
