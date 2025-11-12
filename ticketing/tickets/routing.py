from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/tv/(?P<department_id>\d+)/$', consumers.TVConsumer.as_asgi()),
]