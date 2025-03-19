from rest_framework import serializers
from .models import Review
from freelancia_back_end.serializers import UserSerializer
from freelancia_back_end.models import User
from freelancia_back_end.serializers import UserSerializer as BaseUserSerializer

class UserSerializer(BaseUserSerializer):
    image = serializers.SerializerMethodField()
    def get_image(self, obj):
       return super().get_image(obj)
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name','image') 

class ReviewSerializer(serializers.ModelSerializer):


    user_reviewr_details= UserSerializer (source='user_reviewr', read_only=True)
    user_reviewed_details= UserSerializer(source='user_reviewed', read_only=True)
    user_reviewr = serializers.PrimaryKeyRelatedField(
    queryset=User.objects.all(), write_only=True
)
    user_reviewed = serializers.PrimaryKeyRelatedField(
    queryset=User.objects.all(), write_only=True
)
    class Meta:
        model = Review
        fields = (
            'id',
            'message',
            'rate',
            'project',
            'user_reviewr',
            'user_reviewed',
            'user_reviewr_details',
            'user_reviewed_details',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'user_reviewr_details',
            'user_reviewed_details',
            'created_at',
            'updated_at',
        )
