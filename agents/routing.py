from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/agent/(?P<agent_id>\w+)/$', consumers.AgentTaskConsumer.as_asgi()),
]