from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .models import User , Project , Skill , Proposal

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = '__all__'

class ProjectSerializer(serializers.ModelSerializer):
    # Skills Handeld By A.Abo-ElMagd
    skills = SkillSerializer(many=True, read_only=True)
    required_skills = serializers.SerializerMethodField()

    def get_required_skills(self,obj):
        required_skills = []
        for skill in obj.skills.all():
            required_skills.append(skill.skill)
        return required_skills

    class Meta:
        model = Project
        fields = '__all__'


class ProposalSerializer(serializers.ModelSerializer):
    # user = UserSerializer(read_only=True)
    # project = ProjectSerializer(read_only=True)

    class Meta:
        model = Proposal
        fields = ( 'id', 'price' , 'propose_text' , 'deadline' , 'created_at' , 'project', 'user')

    def validate_price(self, value):
        if value <= 0:
            serializers.ValidationError("Price must be greater than zero")
        return value
    
    def validate_deadline(self, value):
        if value <= 0:
            serializers.ValidationError("Deadline must be greater than zero days")
        return value