from django.urls import re_path
from apps.chat.ws import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/$', consumers.ChatConsumer.as_asgi()),  # URL для WebSocket
]