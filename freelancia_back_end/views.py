from django.shortcuts import render
from django.http import JsonResponse
from .serializers import ProjectSerializer, ProposalSerializer, SkillSerializer, SpecialitySerializer, UserSerializer, CertificateSerializer
from .models import BlackListedToken, Proposal, Skill, Speciality, User, Project, Certificate
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, viewsets
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView
from .permissions import IsOwnerOrAdminOrReadOnly
from django.db import IntegrityError
from rest_framework.exceptions import PermissionDenied
from django.urls import reverse
from .pagination import BasePagination, PaginatedAPIView


class ProjectSearchFilterView(ListAPIView):
    pagination_class = BasePagination

    permission_classes = [AllowAny]
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()

    filter_backends = [SearchFilter, DjangoFilterBackend]
    filterset_fields = ['skills__skill', 'project_state']
    search_fields = ['project_name', 'project_description']

    def get_queryset(self):
        queryset = Project.objects.all()
        search = self.request.GET.get('search', '').strip()
        skills = self.request.GET.get('skills', '').strip().split(',')
        states = self.request.GET.get('states', '').strip().split(',')
        filter_query = Q()
        if skills and not skills == ['']:
            skills_query = Q()
            for skill in skills:
                skills_query |= Q(skills__skill__icontains=skill)
            filter_query &= skills_query
        if states and not states == ['']:
            # print(states)
            states_query = Q()
            for state in states:
                states_query |= Q(project_state__iexact=state)
            filter_query &= states_query
        if search:
            search_query = Q(project_name__icontains=search) | Q(
                project_description__icontains=search)
            filter_query &= search_query
        queryset = queryset.filter(
            filter_query).distinct() if filter_query else queryset

        return queryset


@api_view(['GET'])
@permission_classes([AllowAny])
def proposal_list(request):
    proposals = Proposal.objects.all()
    serializer = ProposalSerializer(
        proposals, many=True, context={'request': request})

    return Response(serializer.data)

# Handle a single proposal


@api_view(['GET'])
@permission_classes([AllowAny])
def proposal_detail(request, id):
    proposal = get_object_or_404(Proposal, id=id)
    serializer = ProposalSerializer(proposal, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def proposal_by_user(request, id):
    user = get_object_or_404(User, id=id)
    proposals = Proposal.objects.filter(user=user)
    serializer = ProposalSerializer(
        proposals, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def proposal_by_project(request, id):
    project = get_object_or_404(Project, id=id)
    proposals = Proposal.objects.filter(project=project)
    serializer = ProposalSerializer(
        proposals, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def userView(request):
    # GET
    if request.method == 'GET':
        username = request.query_params.get('username', None)
        email = request.query_params.get('email', None)
        # Get All Data From User Table
        user = User.objects.all()
        if username:
            user = user.filter(username=username)
        if email:
            user = user.filter(email=email)

        serializer = UserSerializer(
            user, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    # POST
    elif request.method == 'POST':
        serializer = UserSerializer(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Get User By Id


@api_view(['GET', 'PUT', 'DELETE', 'PATCH'])
def userDetailView(request, pk):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UserSerializer(user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        serializer = UserSerializer(
            user, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PATCH':
        if 'image' in request.FILES:
            if user.image:
                user.image.delete()
            user.image = request.FILES['image']
            user.save()
            image = user.image.url if user.image else None
            if image:
                image = request.build_absolute_uri(image)
            return Response({"image": image}, status=status.HTTP_200_OK)
        # print(request.data["delete_image"])
        if "image" in request.data:
            if request.data["image"] == None:
                user.image.delete()
                user.image = None
                user.save()
        serializer = UserSerializer(
            user, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()

            print(serializer.data["image"])
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

# ------------------------------------------------------------------------


User = get_user_model()


class CustomAuthToken(TokenObtainPairView):
    def post(self, request, *args, **kwargs):

        response = super().post(request, *args, **kwargs)

        if response.status_code == status.HTTP_200_OK:
            user = get_object_or_404(User, username=request.data['username'])
            image = user.image.url if user.image else None
            if image:
                image = request.build_absolute_uri(image)
            print(image)
            response.data.update({
                'user_id': user.pk,
                'email': user.email,
                'username': user.username,
                'role': user.role,
                'name': user.name,
                'rate': user.rate,
                'image': image,
                'user_balance': user.user_balance,
            })

        return response

# User Detail View


class UserDetailView(APIView):

    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        return Response({
            'user_id': user.pk,
            'email': user.email,
            'username': user.username,
            'role': user.role,
            'name': user.name,
        })

# ------------------------------------------------------------------------


class ProposalViewAndCreate(PaginatedAPIView):
    permission_classes = [AllowAny]
    serializer_class = ProposalSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsOwnerOrAdminOrReadOnly(owner_field_name='user')]
        return [IsAuthenticated(), IsAdminUser()]

    def get(self, request):
        proposals = Proposal.objects.all()

        user_id = request.query_params.get('user', None)
        project_id = request.query_params.get('project', None)

        if user_id:
            user = get_object_or_404(User, id=user_id)
            proposals = proposals.filter(user=user)
        if project_id:
            project = get_object_or_404(Project, id=project_id)
            proposals = proposals.filter(project=project)

        page = self.paginate_queryset(proposals)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(proposals, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if request.data['project']:
            project = get_object_or_404(Project, id=request.data['project'])
        if serializer.is_valid():
            try:
                serializer.save(user=request.user, project=project)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response(
                    {"error": "You have already submitted a proposal for this project."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        serializer = ProposalSerializer(data=request.data)
        if request.data['project']:
            project = get_object_or_404(Project, id=request.data['project'])
        if serializer.is_valid():
            try:
                serializer.save(user=request.user, project=project)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response(
                    {"error": "You have already submitted a proposal for this project."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProposalAPI(APIView):
    def get_permissions(self):
        print("Applying permissions for method:", self.request.method)
        return [IsOwnerOrAdminOrReadOnly(owner_field_name='user')]

    def get_object(self, id):
        proposal = get_object_or_404(Proposal, id=id)
        self.check_object_permissions(self.request, proposal)
        return proposal

    def get(self, request, id):
        proposal = self.get_object(id)
        serializer = ProposalSerializer(proposal, context={'request': request})
        return Response(serializer.data)

    def put(self, request, id):
        proposal = self.get_object(id)
        serializer = ProposalSerializer(data=request.data, instance=proposal)
        if serializer.is_valid():
            serializer.save(user=proposal.user, project=proposal.project)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, id):
        proposal = self.get_object(id)
        serializer = ProposalSerializer(
            instance=proposal, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        proposal = self.get_object(id)
        proposal.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Project Views
@api_view(['GET'])
@permission_classes([AllowAny])
def ProjectView(request):
    """
    View to list all projects.
    """
    paginator = BasePagination()
    projects = Project.objects.all()
    result_page = paginator.paginate_queryset(projects, request)
    serializer = ProjectSerializer(
        result_page, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)

# Project Views


@api_view(['GET'])
@permission_classes([AllowAny])
def ProjectsPerUser(request):
    """
    View to list projects for:
    - Specific owner_id if provided in query params
    - Request.user if authenticated and no owner_id provided
    - All projects if neither owner_id nor authenticated user
    """
    paginator = BasePagination()
    owner_id = request.query_params.get('owner_id')

    if not owner_id and request.user.is_authenticated:
        owner_id = request.user.id

    if owner_id:
        try:
            owner_id = int(owner_id)
            projects = Project.objects.filter(owner_id=owner_id)
        except (ValueError, TypeError):
            return Response(
                {"error": "owner_id must be a valid integer"},
                status=status.HTTP_400_BAD_REQUEST
            )
    else:
        projects = Project.objects.all()

    result_page = paginator.paginate_queryset(projects, request)
    serializer = ProjectSerializer(
        result_page, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)


# (JJ) Modified this block
class ProjectAPI(APIView):
    permission_classes = [AllowAny]

    def get(self, request, id):
        project = get_object_or_404(Project, id=id)
        serializer = ProjectSerializer(project, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        self.permission_classes = [IsAuthenticated]
        self.check_permissions(request)

        serializer = ProjectSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(owner_id=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id):
        self.permission_classes = [IsAuthenticated]
        self.check_permissions(request)

        project = get_object_or_404(Project, pk=id)

        if project.owner_id != request.user:
            return Response({"error": "Not authorized to modify this project."},
                            status=status.HTTP_403_FORBIDDEN)

        if project.project_state == Project.StatusChoices.ongoing:
            return Response(
                {"error": "Cannot modify a project that is ongoing."},
                status=status.HTTP_400_BAD_REQUEST
            )

        requested_state = request.data.get('project_state')
        if requested_state:
            if project.project_state == Project.StatusChoices.open and \
               requested_state in [Project.StatusChoices.contract_canceled_and_reopened, Project.StatusChoices.finished]:
                 return Response(
                    {"error": f"Cannot change state directly from '{Project.StatusChoices.open}' to '{requested_state}'."},
                    status=status.HTTP_400_BAD_REQUEST
                 )

        serializer = ProjectSerializer(project, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, id):
        self.permission_classes = [IsAuthenticated]
        self.check_permissions(request)

        project = get_object_or_404(Project, pk=id)

        if project.owner_id != request.user:
            return Response({"error": "Not authorized to modify this project."},
                            status=status.HTTP_403_FORBIDDEN)

        if project.project_state == Project.StatusChoices.ongoing:
            return Response(
                {"error": "Cannot modify a project that is ongoing."},
                status=status.HTTP_400_BAD_REQUEST
            )

        requested_state = request.data.get('project_state')
        if requested_state:
            if project.project_state == Project.StatusChoices.open and \
               requested_state in [Project.StatusChoices.contract_canceled_and_reopened, Project.StatusChoices.finished]:
                 return Response(
                    {"error": f"Cannot change state directly from '{Project.StatusChoices.open}' to '{requested_state}'."},
                    status=status.HTTP_400_BAD_REQUEST
                 )

        serializer = ProjectSerializer(
            project, data=request.data, partial=True, context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        self.permission_classes = [IsAuthenticated]
        self.check_permissions(request)

        project = get_object_or_404(Project, pk=id)

        if project.owner_id != request.user:
            return Response({"error": "Not authorized to delete this project."},
                            status=status.HTTP_403_FORBIDDEN)

        if project.project_state == Project.StatusChoices.ongoing:
            return Response(
                {"error": "Cannot delete a project that is ongoing."},
                status=status.HTTP_400_BAD_REQUEST
            )

        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Skill API views
class SkillAPI(APIView):

    def get(self, request, id):

        skill = get_object_or_404(Skill, id=id)
        serializer = SkillSerializer(skill)
        return Response(serializer.data)

    def post(self, request):
        data = request.data
        # print(data)
        serializer = SkillSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id):
        skill = get_object_or_404(Skill, id=id)
        serializer = SkillSerializer(data=request.data, instance=skill)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, id):
        skill = get_object_or_404(Skill, id=id)
        serializer = SkillSerializer(
            instance=skill, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        skill = get_object_or_404(Skill, id=id)
        skill.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Get All Skills


@api_view(['GET'])
@permission_classes([AllowAny])
def skill_list(request):
    """
    View to list all skills.
    """
    skills = Skill.objects.all()
    serializer = SkillSerializer(skills, many=True)
    return Response(serializer.data)

# speciality API view


class SpecialityView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, id=None):
        if id:
            try:
                speciality = Speciality.objects.get(id=id)
                serializer = SpecialitySerializer(speciality)
                return Response(serializer.data)
            except Speciality.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            specialities = Speciality.objects.all()
            serializer = SpecialitySerializer(specialities, many=True)
            return Response(serializer.data)

    def post(self, request):
        user = request.user
        serializer = SpecialitySerializer(data=request.data)
        if user.role == User.RoleChoices.admin:
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        user = request.user
        if user.role == User.RoleChoices.admin:
            user.speciality = request.data['speciality']
            user.save()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        user = request.user
        if user.role == User.RoleChoices.admin:
            user.speciality = request.data['speciality']
            user.save()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user = request.user
        if user.role == User.RoleChoices.admin:
            user.speciality = None
            user.save()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)

# Highest Rated Freelanc View


class HighestRatedFreelancersView(APIView):
    permission_classes = [AllowAny]  # Adjust permissions as needed

    def get(self, request):
        # Filter users with the role 'freelancer' and order by rate in descending order
        freelancers = User.objects.filter(
            role=User.RoleChoices.freelancer).order_by('-rate')[:6]

        # Serialize the filtered users
        serializer = UserSerializer(
            freelancers, many=True, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)


class HighestRatedClientsView(APIView):
    permission_classes = [AllowAny]  # Adjust permissions as needed

    def get(self, request):
        # Filter users with the role 'freelancer' and order by rate in descending order
        clients = User.objects.filter(
            role=User.RoleChoices.client).order_by('-rate')[:4]

        # Serialize the filtered users
        serializer = UserSerializer(
            clients, many=True, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)


# ------------------------------------------------------------------------

class CertificateViewSet(viewsets.ModelViewSet):
    serializer_class = CertificateSerializer

    def get_permissions(self):
        """
        Override get_permissions to allow different permissions per action:
        - List and Retrieve: Allow anyone to view
        - Create, Update, Delete: Require authentication
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Return all certificates for list/retrieve,
        but filter by user for other operations
        """
        if self.action in ['list', 'retrieve']:
            return Certificate.objects.all()
        return Certificate.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        instance = self.get_object()
        if instance.user != self.request.user:
            raise PermissionDenied(
                "You can only update your own certificates.")
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != self.request.user:
            return Response(
                {"detail": "You can only delete your own certificates."},
                status=status.HTTP_403_FORBIDDEN,
            )
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# ------------------------------------------------------------------------
# Display all Urls in list of Json


@api_view(['GET'])
def api_root(request, format=None):

    return Response({
        "certificates": request.build_absolute_uri(reverse('certificate-list')),
        "users": request.build_absolute_uri(reverse('userView')),
        "projects": request.build_absolute_uri(reverse('project_list')),
        "proposals": request.build_absolute_uri(reverse('proposal_list')),
        "skills": request.build_absolute_uri(reverse('skill_list')),
        "speciality": request.build_absolute_uri(reverse('speciality_list')),
    })
