from django.shortcuts import render
from django.http import JsonResponse
from .serializers import ProposalSerializer, UserSerializer
from .models import Proposal, User, Project
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

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
def proposal_by_user(request, id):
    user = get_object_or_404(User, id=id)
    proposals = Proposal.objects.filter(user=user)
    serializer = ProposalSerializer(proposals, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def proposal_by_project(request, id):
    project = get_object_or_404(Project, id=id)
    proposals = Proposal.objects.filter(project=project)
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
