# from channels.generic.websocket import WebsocketConsumer
from channels.generic.websocket import AsyncWebsocketConsumer  # Changed to AsyncWebsocketConsumer
import json
from django.utils import timezone
from channels.db import database_sync_to_async
from django.apps import apps
import logging
from django.core.exceptions import PermissionDenied

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.user = self.scope['user']
            logger.debug(f"User {self.user} attempting to connect")
            
            if not self.user.is_authenticated:
                logger.warning("Connection rejected - user not authenticated")
                await self.close(code=4001)
                return

            query_params = dict(p.split('=') for p in self.scope['query_string'].decode().split('&') if p)
            if 'uuid' not in query_params:
                logger.warning("Connection rejected - no UUID provided")
                await self.close(code=4003)
                return

            self.room_name = self.scope['url_route']['kwargs']['room_name']
            self.room_group_name = f'chat_{self.room_name}'
            
            try:
                self.chat_room, created = await self.get_or_create_chat_room(self.room_name)
                await self.add_user_to_chat_room(self.user, self.chat_room)

                await self.channel_layer.group_add(
                    self.room_group_name,
                    self.channel_name
                )

                await self.accept()
                logger.info(f"User {self.user} connected to room {self.room_name}")

                previous_messages = await self.get_previous_messages(self.room_name)
                for msg in previous_messages:
                    await self.send(text_data=json.dumps({
                    'message': msg.message,
                    'sender': msg.user.username,
                    'message_date': msg.created_at.isoformat(),
                }))

            except Exception as e:
                logger.error(f"Database error: {str(e)}")
                await self.close(code=4005)
                
        except Exception as e:
            logger.error(f"Unexpected connection error: {str(e)}")
            await self.close(code=4000)


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data=None, bytes_data=None):
        json_data = json.loads(text_data)
        message = json_data['message']

        await self.save_message(self.user, self.chat_room, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': self.user.username,
                'message_date': timezone.now().isoformat(),
            }
        )
    
    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        message_date = event['message_date']
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
            'message_date': message_date,
        }))
        
    @database_sync_to_async
    def get_or_create_chat_room(self, room_name):
        ChatRoom = apps.get_model('chat', 'ChatRoom')
        room, created = ChatRoom.objects.get_or_create(
            name=room_name,
            defaults={'owner': self.user}
        )
        
        
        if not room.owner:
            room.owner = self.user
            room.save()
        
        return room, created
    
    @database_sync_to_async
    def add_user_to_chat_room(self, user, chat_room):
        chat_room.participants.add(user)

    @database_sync_to_async
    def save_message(self, user, chat_room, message):
        Message = apps.get_model('chat', 'Message')
        Message.objects.create(
            user=user,
            chat_room=chat_room,
            message=message,
        )
    
    @database_sync_to_async
    def get_previous_messages(self, chat_room, limit=50):
        ChatRoom = apps.get_model('chat', 'ChatRoom')
        Message = apps.get_model('chat', 'Message')
        
        try:
            if isinstance(chat_room, str):
                chat_room = ChatRoom.objects.get(name=chat_room)
            
            return list(Message.objects.filter(chat_room=chat_room)
                            .select_related('user')
                            .order_by('-created_at')[:limit][::-1])
        except ChatRoom.DoesNotExist:
            logger.info("The Chat is Empty")
            return []
        except Exception as e:
            logger.error(f"Error getting messages: {str(e)}")
            return []
        