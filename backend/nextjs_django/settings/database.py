# Database
# https://docs.djangoproject.com/en/dev/ref/settings/#databases

from .env_vars import env

DATABASES = {
    # Raises ImproperlyConfigured exception if DATABASE_URL not in os.environ
    'default': env.db()
}
