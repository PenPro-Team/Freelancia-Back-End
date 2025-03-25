from rest_framework import serializers
from freelancia_back_end.serializers import UserSerializer
from chat.models import ChatRoom
from chat.models import Message 


class ChatRoomSerializer(serializers.ModelSerializer):
    # owner = UserSerializer()
    # participants = UserSerializer()

    class Meta:
        model = ChatRoom
        fields = '__all__'


class MessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = '__all__'

    