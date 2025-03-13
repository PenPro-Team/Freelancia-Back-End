from django.shortcuts import render
from django.http import JsonResponse
import django_filters
from .serializers import ProjectSerializer, ProposalSerializer, UserSerializer
from .models import Proposal, User, Project
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter,OrderingFilter
from rest_framework.views import APIView
from rest_framework import status
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend

# Handles Proposals


@api_view(['GET'])
def proposal_list(request):
    proposals = Proposal.objects.all()
    serializer = ProposalSerializer(proposals, many=True)
    # return JsonResponse({
    #     'data' : serializer.data
    # })
    return Response(serializer.data)

# Handle a single proposal


@api_view(['GET'])
def proposal_detail(request, id):
    # proposal = Proposal.objects.get(id = 'id')
    proposal = get_object_or_404(Proposal, id=id)
    serializer = ProposalSerializer(proposal)
    return Response(serializer.data)


@api_view(['GET'])
def proposal_by_project(request , id):
    project = get_object_or_404(Project , id=id)
    proposals = Proposal.objects.filter(project=project)
    serializer = ProposalSerializer(proposals , many=True)
    return Response(serializer.data)


class ProjectSearchFilterView(ListAPIView):
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()
    
    filter_backends = [SearchFilter, DjangoFilterBackend]
    filterset_fields = ['skills__skill']
    search_fields = ['project_name', 'project_description']

    def get_queryset(self):
        queryset = Project.objects.all()
        search = self.request.GET.get('search', '').strip().lower()
        skills = self.request.GET.get('skills','').strip().lower()

        if search:
            queryset = queryset.filter(Q(project_name__icontains=search) | Q(project_description__icontains=search))
        if skills:
            skills_query = Q()
            for skill in skills:
                skills_query = Q(skills__skill__icontains=skill)
            queryset = queryset.filter(skills_query).distinct()


        return queryset





def proposal_by_user(request, id):
    user = get_object_or_404(User, id=id)
    # proposals = Proposal.objects.filter(user=user)
    proposals = user.proposals.all()
    serializer = ProposalSerializer(proposals, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def proposal_by_project(request, id):
    project = get_object_or_404(Project, id=id)
    # proposals = Proposal.objects.filter(project=project)
    proposals = project.proposals.all()
    print(proposals)
    serializer = ProposalSerializer(proposals, many=True)
    return Response(serializer.data)


@api_view(['GET', 'POST'])
def userView(request):
    # GET
    if request.method == 'GET':
        # Get All Data From User Table
        user = User.objects.all()
        serializer = UserSerializer(user, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    # POST
    elif request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Get User By Id
@api_view(['GET', 'PUT', 'DELETE'])
def userDetailView(request, pk):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProposalView(APIView):
    def get(self, request):
        proposals = Proposal.objects.all()
        serializer = ProposalSerializer(proposals, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProposalSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class ProposalAPI(APIView):
    def get(self, request, id):
        proposal = get_object_or_404(Proposal, id=id)
        serializer = ProposalSerializer(proposal)
        return Response(serializer.data)

    def post(self, request):
        data = request.data
        print(data)
        serializer = ProposalSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id):
        proposal = get_object_or_404(Proposal, id=id)
        serializer = ProposalSerializer(data=request.data, instance=proposal)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, id):
        proposal = get_object_or_404(Proposal, id=id)
        serializer = ProposalSerializer(
            instance=proposal, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        proposal = get_object_or_404(Proposal, id=id)
        proposal.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Project Views
@api_view(['GET'])
def ProjectView(request):
    """
    View to list all projects.
    """
    projects = Project.objects.all()
    serializer = ProjectSerializer(projects, many=True)
    return Response(serializer.data)


class ProjectAPI(APIView):
    """
    API view to handle create, update (PUT/PATCH), and delete operations for Project.
    """
    # Create a new project

    def post(self, request):
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        # Return validation errors if data is not valid
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Full update of a project (replace the entire instance)
    def put(self, request, id):
        project = get_object_or_404(Project, pk=id)
        serializer = ProjectSerializer(project, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Partial update of a project (update only some fields)
    def patch(self, request, id):
        project = get_object_or_404(Project, pk=id)
        serializer = ProjectSerializer(
            project, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Delete a project
    def delete(self, request, id):
        project = get_object_or_404(Project, pk=id)
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
