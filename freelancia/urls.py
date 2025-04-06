"""
URL configuration for freelancia project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from freelancia import settings
from django.conf.urls.static import static

from django_channels_jwt.views import AsgiValidateTokenView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('freelancia_back_end.urls')),
    path('reviews/', include('reviews.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('contract/', include('contract.urls')),
    path('portfolios/', include('portfolio.urls')),
    path('payments/', include('payments.urls')),
    # path('chatauth/' , include('chat.urls')),
    # path("api/auth/chat/", include('django_channels_jwt.urls')),
    path("auth_for_ws_connection/", AsgiValidateTokenView.as_view()),
    path("chat/" , include('chat.urls')),
    path('chatbot/', include('chatbot.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)