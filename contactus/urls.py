from django.urls import path, re_path
from .views import ContactUsAPIView

urlpatterns = [
    path('', ContactUsAPIView.as_view(), name='contactus-list'),
    re_path(r'^(?P<id>\d+)/?$',
            ContactUsAPIView.as_view(), name='contactus'),
]
