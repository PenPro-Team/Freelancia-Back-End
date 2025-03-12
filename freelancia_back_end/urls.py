from django.urls import path

from freelancia_back_end.views import GetAllProjects,SearchProjects, proposal_by_project, proposal_by_user, proposal_detail, proposal_list 

urlpatterns = [
    path('proposals/', proposal_list , name='proposal_list'),
    path('proposals/<int:id>', proposal_detail , name='proposal_detail'),
    path('proposals/user/<int:id>', proposal_by_user , name='user_proposals'),
    path('proposals/project/<int:id>', proposal_by_project , name='project_proposals'),
    path('projects/', GetAllProjects.as_view() , name='projects'),
    path('projects', SearchProjects.as_view(),name="projects"),
]
