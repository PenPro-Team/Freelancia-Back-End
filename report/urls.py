from django.urls import path, re_path
from .views import ReportContractAPIView, ReportContractDetailAPIView, ReportUserAPIView, ReportUserDetailAPIView, UserBanView

urlpatterns = [
    # User Report
    re_path(r'^users/?$', ReportUserAPIView.as_view(),
            name='user-report-list-create'),
    re_path(r'^users/(?P<report_id>\d+)/?$',
            ReportUserDetailAPIView.as_view(), name='user-report-detail'),

    # Contract Report
    re_path(r'^contracts/?$',  ReportContractAPIView.as_view(),
            name='contract-report-list'),
    re_path(r'^contracts/(?P<report_id>\d+)/?$',
            ReportContractDetailAPIView.as_view(), name='contract-report-detail'),

    # User Ban
    path('banned-users/', UserBanView.as_view(), name='banned-users-list'),
    re_path(r'^banned-users/(?P<user_id>\d+)/?$',
            UserBanView.as_view(), name='user-ban'),
]
