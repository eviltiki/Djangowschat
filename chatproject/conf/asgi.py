"""
ASGI config for conf project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conf.settings')
app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from conf.middleware.ws_jwtauth import JWTAuthMiddleware
import apps.chat.ws.routing

application = ProtocolTypeRouter({
    "http": app,
    "websocket": AuthMiddlewareStack(
        JWTAuthMiddleware(
            URLRouter(
                apps.chat.ws.routing.websocket_urlpatterns
            )
        )
    )
})