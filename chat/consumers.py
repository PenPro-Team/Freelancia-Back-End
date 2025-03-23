from channels.generic.websocket import WebsocketConsumer
import json
from django.utils import timezone
from .models import ChatRoom , Message
from freelancia_back_end.models import User
from channels.db import database_sync_to_async


class ChatConsumer(WebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        print("User Tries to Connect: ", self.user)

        if not self.user.is_authenticated:
            await self.close()
            return

        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        
        self.chat_room, created = await self.get_or_create_chat_room(self.room_name)
        await self.add_user_to_chat_room(self.user, self.chat_room)

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        
        await self.accept()
        

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
            )
    
    async def receive(self, text_data=None, bytes_data=None):
        json_data = json.load(text_data)
        message = json_data['message']

        await self.save_message(self.user, self.chat_room, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': self.user.username,
                'message_date':timezone.now().isoformat(),
            }
            )
    
    async def chat_message(self , event):
        message = event['message']
        sender = event['sender']
        message_date = event['message_data']
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
            'message_date': message_date,
            }))
        
    @database_sync_to_async
    def get_or_create_chat_room(self, room_name):
        return ChatRoom.objects.get_or_create(name=room_name)
    
    @database_sync_to_async
    def add_user_to_chat_room(self , user , chat_room):
        chat_room.participants.add(user)

    @database_sync_to_async
    def save_message(self , user , chat_room , message):
        Message.objects.create(
            user=user,
            chat_room=chat_room,
            message=message,
            )
    