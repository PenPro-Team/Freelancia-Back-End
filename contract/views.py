from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Contract
from .serializers import ContractSerializer
from freelancia_back_end.models import User, Project
from .notifications import send_contract_notification  # Import the function from notifications.py (email notifications)

@api_view(['POST'])
def create_contract(request):
    client_id = request.data.get('client')
    freelancer_id = request.data.get('freelancer')
    project_id = request.data.get('project') 

    if client_id is None or freelancer_id is None or project_id is None:
        return Response({'message': 'Please provide all the required fields'}, status=status.HTTP_400_BAD_REQUEST)
    
    creator = User.objects.get(id=client_id)
    assined = User.objects.get(id=freelancer_id)

    if creator.role != 'client' or assined.role != 'freelancer':
        return Response({'message': 'The creator must be a client and the assined must be a freelancer'}, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = ContractSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        contract = serializer.save()
        send_contract_notification(contract, event='created')  # Send notification email
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response({
        'message': 'Failed to create contract',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_user_contracts(request, user_id):
    if not user_id:
        return Response({'message': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.user.id != user.id and request.user.role != 'admin':
        return Response({'message': 'You are not authorized to view these contracts'}, status=status.HTTP_403_FORBIDDEN)

    contracts = Contract.objects.filter(client=user) | Contract.objects.filter(freelancer=user)
    serializer = ContractSerializer(contracts, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_contract(request, contract_id):
    if not contract_id:
        return Response({'message': 'Contract ID is required'}, status=status.HTTP_400_BAD_REQUEST)
    contract = get_object_or_404(Contract, id=contract_id)
    serializer = ContractSerializer(contract, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PATCH'])
def update_contract(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id)
    print(f"Request User: {request.user}")
    print(f"Contract Freelancer: {contract.freelancer}")
    print(f"Contract Client: {contract.client}")

    # Block any updates if contract isn't in 'pending' state
    if contract.contract_state != 'pending':
        return Response({'message': 'You cannot update this contract'}, status=status.HTTP_400_BAD_REQUEST)

    # FREELANCER: Can ONLY update 'contract_state'
    if contract.freelancer == request.user:
        allowed_fields = {'contract_state'}
        request_fields = set(request.data.keys())
        if not request_fields.issubset(allowed_fields):
            return Response({'message': 'Freelancers can only update contract_state'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ContractSerializer(contract, data=request.data, partial=True, context={'request': request})
    # CLIENT: Can update anything EXCEPT 'contract_state'
    elif contract.client == request.user:
        if 'contract_state' in request.data:
            return Response({'message': 'Clients are not allowed to update contract_state'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ContractSerializer(contract, data=request.data, partial=True, context={'request': request})
    else:
        return Response({'message': 'You are not authorized to update this contract'}, status=status.HTTP_403_FORBIDDEN)

    if serializer.is_valid():
        contract = serializer.save()
        send_contract_notification(contract, event=contract.contract_state)  # Send notification email based on new state
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_contract(request, contract_id):
    if request.user.role != 'admin':
        return Response({'message': 'You are not authorized to delete this contract'}, status=status.HTTP_403_FORBIDDEN)
    contract = get_object_or_404(Contract, id=contract_id)
    contract.delete()
    return Response({'message': 'Contract deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
