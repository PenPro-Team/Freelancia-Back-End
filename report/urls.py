from django.urls import path, re_path
from .views import ReportUserAPIView, ReportUserDetailAPIView

urlpatterns = [
    re_path(r'^users/?$', ReportUserAPIView.as_view(),
            name='report-list-create'),
    re_path(r'^users/(?P<report_id>\d+)/?$',
            ReportUserDetailAPIView.as_view(), name='report-detail'),
]
