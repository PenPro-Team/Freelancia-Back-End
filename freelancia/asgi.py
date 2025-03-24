"""
ASGI config for freelancia project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""
import os
import logging
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

# Ensure the settings module is set
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freelancia.settings')

# Initialize Django apps
import django
django.setup()

# Import JwtAuthMiddlewareStack and routing after Django setup
# from django_channels_jwt.middleware import JwtAuthMiddlewareStack
# from django_channels_jwt_auth_middleware.auth import JWTAuthMiddlewareStack
from django_channels_jwt.middleware import JwtAuthMiddlewareStack
from chat.routing import websocket_urlpatterns

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("Starting ASGI application")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JwtAuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})

logger.debug("ASGI application configured")