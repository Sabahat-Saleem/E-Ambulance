import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'E_ambulance.settings')  # 👈 must be before Django imports

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

import ambulance.routing
   # your app’s routing.py

# ✅ Set Django settings before calling get_asgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'E_ambulance.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            ambulance.routing.websocket_urlpatterns
        )
    ),
})
