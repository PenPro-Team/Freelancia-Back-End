from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    # user_reviewr = serializers.StringRelatedField(read_only=True)
    # user_reviewed = serializers.StringRelatedField(read_only=True)
    # project = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Review
        fields = '__all__'
