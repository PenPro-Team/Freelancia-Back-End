import logging
logger = logging.getLogger(__name__)

from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, parser_classes
from .models import Attachment, Contract
from .serializers import AttachmentSerializer, ContractSerializer
from freelancia_back_end.models import User, Project
from .notifications import send_contract_notification  # Import the function from notifications.py (email notifications)
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import transaction
from decimal import Decimal

@api_view(['POST'])
def create_contract(request):
    logger.info(f"Attempting to create contract with data: {request.data}")
    client_id = request.data.get('client')
    freelancer_id = request.data.get('freelancer')
    project_id = request.data.get('project')
    budget = request.data.get('budget')

    if client_id is None or freelancer_id is None or project_id is None or budget is None:
        logger.error(f"Missing required fields in contract creation: {request.data}")
        return Response({'message': 'Please provide all the required fields'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        creator = User.objects.get(id=client_id)
        assined = User.objects.get(id=freelancer_id)

        if creator.role != 'client' or assined.role != 'freelancer':
            logger.error(f"Invalid roles: creator={creator.role}, assigned={assined.role}")
            return Response({'message': 'The creator must be a client and the assined must be a freelancer'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        budget_decimal = Decimal(str(budget))
        logger.info(f"Checking balance for client {creator.username}: required={budget_decimal}, current={creator.user_balance}")
        
        if creator.user_balance < budget_decimal:
            logger.warning(f"Insufficient funds for client {creator.username}")
            return Response({
                'message': 'Insufficient funds! Please Deposit enough money to create a contract',
                'required_amount': float(budget_decimal),
                'current_balance': float(creator.user_balance)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            creator.user_balance -= budget_decimal
            creator.save()
            
            serializer = ContractSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                logger.info("Contract data validated successfully")
                contract = serializer.save()
                send_contract_notification(contract, event='created')
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                logger.error(f"Contract validation failed: {serializer.errors}")
                return Response({
                    'message': 'Failed to create contract',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
    except User.DoesNotExist as e:
        logger.error(f"User not found error: {str(e)}")
        return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Unexpected error in contract creation: {str(e)}", exc_info=True)
        return Response({
            'message': 'Failed to create contract',
            'error': str(e)
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
        
        try:
            with transaction.atomic():
                serializer = ContractSerializer(contract, data=request.data, partial=True, context={'request': request})
                if serializer.is_valid():
                    new_state = request.data.get('contract_state')
                    budget_decimal = Decimal(str(contract.budget))  # Convert to Decimal safely
                    
                    if new_state == 'finished':
                        # Transfer using Decimal
                        freelancer = contract.freelancer
                        freelancer.user_balance += budget_decimal
                        freelancer.save()
                    elif new_state == 'canceled':
                        # Refund using Decimal
                        client = contract.client
                        client.user_balance += budget_decimal
                        client.save()
                        
                    contract = serializer.save()
                    send_contract_notification(contract, event=contract.contract_state)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'message': f'Error processing payment: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

    # CLIENT: Can update anything EXCEPT 'contract_state'
    elif contract.client == request.user:
        if 'contract_state' in request.data and request.data['contract_state'] != 'finished':
            return Response({'message': 'Clients are not allowed to update contract_state'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ContractSerializer(contract, data=request.data, partial=True, context={'request': request})
    else:
        return Response({'message': 'You are not authorized to update this contract'}, status=status.HTTP_403_FORBIDDEN)

    if serializer.is_valid():
        contract = serializer.save()
        send_contract_notification(contract, event=contract.contract_state)
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_contract(request, contract_id):
    if request.user.role != 'admin':
        return Response({'message': 'You are not authorized to delete this contract'}, status=status.HTTP_403_FORBIDDEN)
    contract = get_object_or_404(Contract, id=contract_id)
    contract.delete()
    return Response({'message': 'Contract deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])  
def upload_attachment(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id)
    if request.user != contract.freelancer:
        return Response({'message': 'You are not authorized to upload attachments for this contract'}, status=status.HTTP_403_FORBIDDEN)

    files = request.FILES.getlist('files')
    if not files:
        return Response({'message': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    uploaded_files = []
    for file in files:
        # if file.name.split('.')[-1] not in ['pdf', 'docx', 'txt', 'jpg', 'jpeg', 'png', 'py','']:
        #     return Response({'message': f'File {file.name} is not a valid file type'}, status=status.HTTP_400_BAD_REQUEST)
        
        
        if file.size > 10 * 1024 * 1024: 
            return Response({'message': f'File {file.name} is too large'},  status=status.HTTP_400_BAD_REQUEST)
        
        attachment = Attachment.objects.create(file=file, contract=contract)
        uploaded_files.append(attachment)
    serializer = AttachmentSerializer(uploaded_files, context={'request': request}, many=True)
    return Response(serializer.data, status=status.HTTP_201_CREATED)