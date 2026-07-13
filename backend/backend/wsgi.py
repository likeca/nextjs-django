"""
For local development "python manage.py runserver"
"""
import os

if os.environ.get("DJANGO_ENVIRONMENT") == "Development":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings.environments.development")
elif os.environ.get("DJANGO_ENVIRONMENT") == "Container":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings.environments.container")
else:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings.environments.virtualmachine")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()


# Wrap werkzeug debugger if DEBUG is on
from django.conf import settings

if settings.DEBUG:
    try:
        import django.views.debug
        import six
        from werkzeug.debug import DebuggedApplication

        def null_technical_500_response(request, exc_type, exc_value, tb):
            six.reraise(exc_type, exc_value, tb)

        django.views.debug.technical_500_response = null_technical_500_response
        application = DebuggedApplication(
            application,
            evalex=True,
            # Turning off pin security as DEBUG is True
            pin_security=False,
        )
    except ImportError:
        pass
