from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import ChatRoom
from .models import Message
from django.db.models import Q
from .serializers import ChatRoomSerializer
from .serializers import MessageSerializer
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from freelancia_back_end.models import User
# Create your views here.
class UserChatRoomList(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        chat_rooms = ChatRoom.objects.filter(Q(owner = user) | Q(participants=user)).distinct().order_by('-updated_at')
        serializer = ChatRoomSerializer(chat_rooms , many = True ,  context={'request': request})
        return Response(serializer.data , status=status.HTTP_200_OK)
    
    def post(self,request):
        room_name = request.data.get('name')
        participants_ids = request.data.get('participants', [])

        if room_name:
            chat_room, created = ChatRoom.objects.get_or_create(
                name=room_name,
                defaults={'owner': request.user}
            )

            participants = User.objects.filter(id__in=participants_ids)
            chat_room.participants.add(*participants)

            if not created:
                chat_room.participants.add(request.user)

            serializer = ChatRoomSerializer(chat_room, context={'request': request})
            return Response(serializer.data , status=status.HTTP_200_OK)



class ChatRoomMessagesList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request, chat_room):
        chat_room = get_object_or_404(ChatRoom , name = chat_room)
        if chat_room:
            if request.user in chat_room.participants | request.user == chat_room.owner:
                messages = chat_room.messages.all().order_by('created_at')
                serializer = MessageSerializer(messages , many=True)
                Response(serializer.data , status=status.HTTP_200_OK)
            else:
                content = {"message" , "You don't have the access to this chat"}
                Response(content , status=status.HTTP_403_FORBIDDEN)
        else:
            content = {"message" , "There's no chat room with that name"}
            Response(content , status=status.HTTP_404_NOT_FOUND)

            
