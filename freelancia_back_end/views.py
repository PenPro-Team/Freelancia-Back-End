from django.shortcuts import render
from django.http import JsonResponse
from .serializers import ProjectSerializer, ProposalSerializer
from .models import Proposal , User , Project
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import status

# Handles Proposals
@api_view(['GET'])
def proposal_list(request):
    proposals = Proposal.objects.all()
    serializer = ProposalSerializer(proposals , many=True)
    # return JsonResponse({
    #     'data' : serializer.data
    # })
    return Response(serializer.data)

# Handle a single proposal
@api_view(['GET'])
def proposal_detail(request,id):
    # proposal = Proposal.objects.get(id = 'id')
    proposal = get_object_or_404(Proposal, id=id)
    serializer = ProposalSerializer(proposal)
    return Response(serializer.data)

@api_view(['GET'])
def proposal_by_user(request , id):
    user = get_object_or_404(User , id=id)
    # proposals = Proposal.objects.filter(user=user)
    proposals = user.proposals.all()
    serializer = ProposalSerializer(proposals , many=True)
    return Response(serializer.data)

@api_view(['GET'])
def proposal_by_project(request , id):
    project = get_object_or_404(Project , id=id)
    # proposals = Proposal.objects.filter(project=project)
    proposals = project.proposals.all()
    print(proposals)
    serializer = ProposalSerializer(proposals , many=True)
    return Response(serializer.data)

class ProposalView(APIView):
    def get(self , request):
        proposals = Proposal.objects.all()
        serializer = ProposalSerializer(proposals , many=True)
        return Response(serializer.data)
    
    def post(self , request):
        serializer = ProposalSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data , status=201)
        return Response(serializer.errors , status=400)
    
class ProposalAPI(APIView):
    def get(self , request , id):
        proposal = get_object_or_404(Proposal , id=id)
        serializer = ProposalSerializer(proposal)
        return Response(serializer.data)
    
    def post(self ,request):
        data = request.data
        print(data)
        serializer = ProposalSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data , status=201)
        return Response(serializer.errors , status=status.HTTP_400_BAD_REQUEST)
    
    def put(self , request , id):
        proposal = get_object_or_404(Proposal , id=id)
        serializer = ProposalSerializer(data=request.data , instance = proposal)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors , status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self , request , id):
        proposal = get_object_or_404(Proposal , id=id)
        serializer = ProposalSerializer(instance = proposal , data=request.data , partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors , status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request , id):
        proposal = get_object_or_404(Proposal , id=id)
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
        serializer = ProjectSerializer(project, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Delete a project
    def delete(self, request, id):
        project = get_object_or_404(Project, pk=id)
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)