from rest_framework import serializers
from freelancia_back_end.serializers import UserSerializer
from chat.models import ChatRoom
from chat.models import Message 


class ChatRoomSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()
    participants = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = '__all__'

    def get_owner(self, obj):
        request = self.context.get('request')
        return UserSerializer(obj.owner, context={'request': request}).data if request else UserSerializer(obj.owner).data

    def get_participants(self, obj):
        request = self.context.get('request')
        return UserSerializer(obj.participants.all(), many=True, context={'request': request}).data if request else UserSerializer(obj.participants.all(), many=True).data


class MessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = '__all__'

    