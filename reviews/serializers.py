from rest_framework import serializers
from .models import Review
from freelancia_back_end.serializers import UserSerializer
from freelancia_back_end.models import User
from freelancia_back_end.serializers import UserSerializer as BaseUserSerializer

class UserSerializer(BaseUserSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name','image') 

class ReviewSerializer(serializers.ModelSerializer):

    user_reviewr= UserSerializer (read_only=True)
    user_reviewed= UserSerializer(read_only=True)
    class Meta:
        model = Review
        fields = '__all__'
