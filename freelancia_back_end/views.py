from django.shortcuts import render
from django.http import JsonResponse
from .serializers import ProposalSerializer
from .models import Proposal , User , Project
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

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
    proposals = Proposal.objects.filter(user=user)
    serializer = ProposalSerializer(proposals , many=True)
    return Response(serializer.data)

@api_view(['GET'])
def proposal_by_project(request , id):
    project = get_object_or_404(Project , id=id)
    proposals = Proposal.objects.filter(project=project)
    serializer = ProposalSerializer(proposals , many=True)
    return Response(serializer.data)