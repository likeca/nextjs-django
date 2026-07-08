"""
ASGI config for deployment and production.

It exposes the ASGI callable as a module-level variable named ``application``.
For more information on this file, see
https://docs.djangoproject.com/en/dev/howto/deployment/asgi/
"""
import os

if os.environ.get("DJANGO_ENVIRONMENT") == "Development":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nextjs_django.settings.environments.development")
elif os.environ.get("DJANGO_ENVIRONMENT") == "VirtualMachine":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nextjs_django.settings.environments.virtualmachine")
else:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nextjs_django.settings.environments.container")

from django.core.asgi import get_asgi_application

# HTTP
application = get_asgi_application()

# HTTP & WebSocket
# from channels.auth import AuthMiddlewareStack
# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.security.websocket import AllowedHostsOriginValidator
# import chat.routing

# django_asgi_app = get_asgi_application()
# application = ProtocolTypeRouter(
#     {
#         # Need to separate HTTP & Websocket
#         "http": django_asgi_app,
#         "websocket": AllowedHostsOriginValidator(AuthMiddlewareStack(URLRouter(chat.routing.websocket_urlpatterns))),
#     }
# )
