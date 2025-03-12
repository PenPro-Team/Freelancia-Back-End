from django.urls import path
from . import views

from freelancia_back_end.views import proposal_by_project, proposal_by_user, proposal_detail, proposal_list, userView

urlpatterns = [
    path('proposals/', proposal_list, name='proposal_list'),
    path('proposals/<int:id>', proposal_detail, name='proposal_detail'),
    path('proposals/user/<int:id>', proposal_by_user, name='user_proposals'),
    path('proposals/project/<int:id>',
         proposal_by_project, name='project_proposals'),
    path('api/v1/user/', userView, name='userView'),
    path('api/v1/user/<int:pk>/', views.userDetailView),
]
