from django.shortcuts import render
from django.http import JsonResponse
from .serializers import ProjectSerializer, ProposalSerializer, SkillSerializer, UserSerializer
from .models import BlackListedToken, Proposal, Skill, User, Project
from rest_framework.decorators import api_view , permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated , AllowAny , IsAdminUser

from .permissions import IsOwnerOrAdminOrReadOnly
from django.db import IntegrityError

# Handles Proposals


@api_view(['GET'])
def proposal_list(request):
    proposals = Proposal.objects.all()
    serializer = ProposalSerializer(proposals, many=True , context={'request': request})
    # return JsonResponse({
    #     'data' : serializer.data
    # })
    return Response(serializer.data)

# Handle a single proposal


@api_view(['GET'])
def proposal_detail(request, id):
    # proposal = Proposal.objects.get(id = 'id')
    proposal = get_object_or_404(Proposal, id=id)
    serializer = ProposalSerializer(proposal , context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
def proposal_by_project(request, id):
    project = get_object_or_404(Project, id=id)
    proposals = Proposal.objects.filter(project=project)
    serializer = ProposalSerializer(proposals, many=True , context={'request': request})
    return Response(serializer.data)


class ProjectSearchFilterView(ListAPIView):
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
        # state_query = Q()
        filter_query = Q()
        # skills_query = Q()
        # print(filter_query)
        if skills and not skills == ['']:
            # print(skills)
            skills_query = Q()
            for skill in skills:
                skills_query |= Q(skills__skill__icontains=skill)
            filter_query &= skills_query
            # queryset = queryset.filter(skills_query).distinct()
        if states and not states == ['']:
            # print(states)
            states_query = Q()
            for state in states:
                states_query |= Q(project_state__iexact=state)
            filter_query &= states_query
            # queryset = queryset.filter(state_query).distinct()
        if search:
            search_query = Q(project_name__icontains=search) | Q(
                project_description__icontains=search)
            filter_query &= search_query
            # queryset = queryset.filter(Q(project_name__icontains=search) | Q(project_description__icontains=search))
        # print(filter_query)
        queryset = queryset.filter(
            filter_query).distinct() if filter_query else queryset

        return queryset


@api_view(['GET'])
def proposal_by_user(request, id):
    user = get_object_or_404(User, id=id)
    proposals = Proposal.objects.filter(user=user)
    # proposals = user.proposals.all()
    serializer = ProposalSerializer(proposals, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
def proposal_by_project(request, id):
    project = get_object_or_404(Project, id=id)
    proposals = Proposal.objects.filter(project=project)
    # proposals = project.proposals.all()
    # print(proposals)
    serializer = ProposalSerializer(proposals, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET', 'POST'])
def userView(request):
    # GET
    if request.method == 'GET':
        # Get All Data From User Table
        user = User.objects.all()
        serializer = UserSerializer(user, many=True , context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    # POST
    elif request.method == 'POST':
        serializer = UserSerializer(data=request.data)
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
        serializer = UserSerializer(user , context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PATCH':
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
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


class ProposalViewAndCreate(APIView):
    # permission_classes = [AllowAny]
    
    # def get_permissions(self):
    #     self.permission_classes = [AllowAny]
    #     if self.request.method == 'POST':
    #         self.permission_classes = [IsAuthenticated , IsAdminUser]
    #     return super().get_permissions()

    def get_permissions(self):
        return [IsOwnerOrAdminOrReadOnly(owner_field_name='user')]

    def get(self, request):
        proposals = Proposal.objects.all()

        user_id = request.query_params.get('user' , None)
        project_id = request.query_params.get('project' , None)

        if user_id:
            user = get_object_or_404(User, id=user_id)
            proposals = proposals.filter(user=user)
        if project_id:
            project = get_object_or_404(Project, id=project_id)
            proposals = proposals.filter(project=project)
        serializer = ProposalSerializer(proposals, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        self.permission_classes = [IsAuthenticated , IsAdminUser]
        serializer = ProposalSerializer(data=request.data)
        if request.data['project']:
            project = get_object_or_404(Project, id=request.data['project'])
        if serializer.is_valid():
            try:
                # Save the proposal with the logged-in user and project
                serializer.save(user=request.user, project=project)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except IntegrityError:
                # Handle the case where a proposal already exists for this user and project
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
        serializer = ProposalSerializer(instance=proposal, data=request.data, partial=True)
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
@permission_classes([IsAuthenticated])
def ProjectView(request):
    """
    View to list all projects.
    """
    projects = Project.objects.all()
    serializer = ProjectSerializer(projects, many=True, context={'request': request})
    return Response(serializer.data)


class ProjectAPI(APIView):
    """
    API view to handle create, update (PUT/PATCH), and delete operations for Project.
    """
    # Get One Project Detail
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        project = get_object_or_404(Project, id=id)
        serializer = ProjectSerializer(project , context={'request': request})
        return Response(serializer.data)

    # Create a new project

    def post(self, request):
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner_id=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        # Return validation errors if data is not valid
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Full update of a project (replace the entire instance)
    def put(self, request, id):
        project = get_object_or_404(Project, pk=id)
        # owner check
        if project.owner_id != request.user:
            return Response({"error": "Not authorized"}, status=403)
        serializer = ProjectSerializer(project, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Partial update of a project (update only some fields)
    def patch(self, request, id):
        project = get_object_or_404(Project, pk=id)
        # owner check
        if project.owner_id != request.user:
            return Response({"error": "Not authorized"}, status=403)
        serializer = ProjectSerializer(
            project, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Delete a project
    def delete(self, request, id):
        project = get_object_or_404(Project, pk=id)
        # owner check
        if project.owner_id != request.user:
            return Response({"error": "Not authorized"}, status=403)
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Skill API views
class SkillAPI(APIView):
    permission_classes = [IsAuthenticated , IsAdminUser]

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
def skill_list(request):
    """
    View to list all skills.
    """
    skills = Skill.objects.all()
    serializer = SkillSerializer(skills, many=True)
    return Response(serializer.data)
