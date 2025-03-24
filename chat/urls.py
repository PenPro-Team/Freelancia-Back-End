from django.urls import path, include
from django_channels_jwt.views import AsgiValidateTokenView

url_patterns = [
    path("api/auth/", include('django_channels_jwt.urls')),
    path("auth_for_ws_connection/", AsgiValidateTokenView.as_view()),
]
