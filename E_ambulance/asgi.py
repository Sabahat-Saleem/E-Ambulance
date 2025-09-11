import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "E_ambulance.settings")

# 👇 Important: Django ko initialize karo models import se pehle
django.setup()

import ambulance.routing   # ab safe hai

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            ambulance.routing.websocket_urlpatterns
        )
    ),
})
