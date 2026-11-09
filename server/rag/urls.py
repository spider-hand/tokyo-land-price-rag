from django.urls import path

from .views import health, messages

urlpatterns = [
    path("health/", health, name="health"),
    path("messages/", messages, name="messages"),
]
