from django.urls import path
from . import views

from freelancia_back_end.views import ProjectAPI, ProjectView, ProposalAPI, proposal_by_project, proposal_by_user, proposal_detail, proposal_list, userView

urlpatterns = [
    path('proposals/', proposal_list, name='proposal_list'),
    path('proposals/<int:id>', proposal_detail, name='proposal_detail'),
    path('proposals/user/<int:id>', proposal_by_user, name='user_proposals'),
    path('proposals/project/<int:id>',
         proposal_by_project, name='project_proposals'),
    path('proposal/', ProposalAPI.as_view(), name='proposal_api_create'),
    path('proposal/<int:id>', ProposalAPI.as_view(), name='proposal_api'),
    # view For User Oprations
    path('api/v1/user/', userView, name='userView'),
    path('api/v1/user/<int:pk>/', views.userDetailView),
    # Project Urls Handling
    # List view for all projects
    path('projects/', ProjectView, name='project_list'),
    # API endpoint for create operation
    path('project/', ProjectAPI.as_view(), name='project_api_create'),
    # API endpoint for update (PUT/PATCH) and delete operations on a specific project
    path('project/<int:id>/', ProjectAPI.as_view(), name='project_api'),
]
