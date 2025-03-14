from django.urls import path
from . import views

from freelancia_back_end.views import LogoutView, ProjectSearchFilterView, ProjectAPI, ProjectView, ProposalAPI, SkillAPI, proposal_by_project, proposal_by_user, proposal_detail, proposal_list, skill_list, userView

urlpatterns = [
    # Proposal Read (get) API
    path('proposals/', proposal_list, name='proposal_list'),
    path('proposals/<int:id>', proposal_detail, name='proposal_detail'),
    path('proposals/user/<int:id>', proposal_by_user, name='user_proposals'),
    path('proposals/project/<int:id>',
         proposal_by_project, name='project_proposals'),
    # Proposal Post API
    path('proposals/create', ProposalAPI.as_view(), name='proposal_api_create'),
    # Prpoposal READ Write GET
    path('proposals/<int:id>', ProposalAPI.as_view(), name='proposal_api'),
    # view For User Oprations
    path('users/', userView, name='userView'),
    path('users/<int:pk>', views.userDetailView),
    # Project Urls Handling
    # List view for all projects
    path('projects/', ProjectView, name='project_list'),
    path('projects/search/', ProjectSearchFilterView.as_view(),
         name="projects-search-filter"),
    # API endpoint for create operation
    path('projects/create/', ProjectAPI.as_view(), name='project_api_create'),
    # API endpoint for update (PUT/PATCH) and delete operations on a specific project
    path('projects/<int:id>', ProjectAPI.as_view(), name='project_api'),
    # Api Gets All the Skills
    path('skills/', skill_list, name='skill_list'),
    # Api Get Push and Delete the Skill
    path('skills/<int:id>', SkillAPI.as_view(), name='skill_api'),
    # Api Post the Skill
    path('skills/create/', SkillAPI.as_view(), name='skill_post'),
    # logout endpoint
    path('logout/', LogoutView.as_view(), name='auth_logout'),
]
