from django.urls import path, re_path
from .views import ReportUserAPIView, ReportUserDetailAPIView, UserBanView

urlpatterns = [
    re_path(r'^users/?$', ReportUserAPIView.as_view(),
            name='report-list-create'),
    re_path(r'^users/(?P<report_id>\d+)/?$',
            ReportUserDetailAPIView.as_view(), name='report-detail'),
    path('banned-users/', UserBanView.as_view(), name='banned-users-list'),
    re_path(r'^banned-users/(?P<user_id>\d+)/?$',
            UserBanView.as_view(), name='user-ban'),
]
