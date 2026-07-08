# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/
from django.utils.translation import gettext_lazy as _
from .env_vars import BASE_DIR

# Default data format: 2000-02-18
USE_L10N = True
USE_I18N = True
USE_TZ = True
TIME_ZONE = 'America/Toronto'

# Language
LOCALE_PATHS = (BASE_DIR.joinpath('locale'),)
LANGUAGE_CODE = 'en'
LANGUAGES = (
    ('en', _('English')),
    ('fr', _('French')),
    ('zh-hans', _('Simplified Chinese')),
)
