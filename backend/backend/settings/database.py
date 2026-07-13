# Database
# https://docs.djangoproject.com/en/dev/ref/settings/#databases

from .env_vars import env

DATABASES = {
    # Raises ImproperlyConfigured exception if DATABASE_URL not in os.environ
    'default': env.db()
}

# Persistent connections Prisma DB: without this every request pays a fresh TCP/TLS/auth
# handshake to Postgres (a remote pooled host here, so it's expensive).
DATABASES['default']['CONN_MAX_AGE'] = env.int('CONN_MAX_AGE', default=60)
DATABASES['default']['CONN_HEALTH_CHECKS'] = True
