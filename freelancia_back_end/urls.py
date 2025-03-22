from django.urls import include, path
from . import views
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static
from freelancia_back_end.views import CertificateViewSet, CustomAuthToken, HighestRatedClientsView, HighestRatedFreelancersView, LogoutView, SpecialityView, ProjectSearchFilterView, ProjectAPI, ProjectView, ProposalAPI, ProposalViewAndCreate, SkillAPI, UserDetailView, proposal_by_project, proposal_by_user, proposal_detail, proposal_list, skill_list, userView

router = DefaultRouter()
router.register(r'certificates', CertificateViewSet, basename='certificate')

urlpatterns = [
    # Proposal Read (get) API
    #     path('proposals/', proposal_list, name='proposal_list'),
    #     path('proposals/<int:id>', proposal_detail, name='proposal_detail'),
    path('proposals/', ProposalViewAndCreate.as_view(), name='proposal_list'),
    path('proposals/user/<int:id>', proposal_by_user, name='user_proposals'),
    path('proposals/project/<int:id>',
         proposal_by_project, name='project_proposals'),
    # Proposal Post API
    #     path('proposals/create', ProposalAPI.as_view(), name='proposal_api_create'),
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
    # Custom Auth Token
    path('auth-token/', CustomAuthToken.as_view(), name='auth_token'),
    # GET User Detail
    path('user/<int:pk>/', UserDetailView.as_view(), name='user_detail'),
    path('speciality/', SpecialityView.as_view(), name='speciality_list'),
    path('speciality/<int:id>/', SpecialityView.as_view(), name='speciality_api'),
    path('freelancers/highest-rated/', HighestRatedFreelancersView.as_view(),
         name='highest_rated_freelancers'),
    path('clients/highest-rated/', HighestRatedClientsView.as_view(),
         name='highest_rated_clients'),

    # Certificates endpoints
    path('certificates/', CertificateViewSet.as_view(
        {'get': 'list', 'post': 'create'}), name='certificate_list'),
    path('certificates/<int:id>/', CertificateViewSet.as_view(
        {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='certificate_detail'),

    path('', include(router.urls)),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
