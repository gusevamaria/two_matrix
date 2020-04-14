#from channels.routing import route_class
from .consumers import TaskTracker
from django.urls import re_path

#channel_routing = [route_class(TaskTracker, path=TaskTracker.url_pattern), ]
websocket_routes = [re_path(TaskTracker.url_pattern, TaskTracker), ]
