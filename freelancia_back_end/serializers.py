from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view

from freelancia import settings

from .models import Speciality, User , Project , Skill , Proposal

from django.conf import settings
from urllib.parse import urljoin

from django.contrib.auth.hashers import make_password

class SpecialitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Speciality
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    speciality_details = SpecialitySerializer(source='speciality', read_only=True)
    speciality = serializers.PrimaryKeyRelatedField(
        queryset=Speciality.objects.all(),
        required=False,
        allow_null=True
    )
    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            else:
                return urljoin(settings.MEDIA_URL, str(obj.image))
        return None

    def get_name(self,obj):
        if obj.name:
            return obj.name
        else:
            return ""


    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = (
            'id',
            'is_staff',
            'is_superuser',
            'is_active',
            'created_at',
            'updated_at',
            'rate',
            'total_user_rated',
            'groups',
            'user_permissions',
            'name',
        )
    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data.get('password'))
        return super().create(validated_data)

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = '__all__'

class ProjectSerializer(serializers.ModelSerializer):
    # Dont Edit For A.A.A
    skills = SkillSerializer(many=True, read_only=True)
    skills_ids = serializers.PrimaryKeyRelatedField(
        queryset=Skill.objects.all(), many=True, write_only=True
    )
    required_skills = serializers.SerializerMethodField()

    def get_required_skills(self,obj):
        required_skills = []
        for skill in obj.skills.all():
            required_skills.append(skill.skill)
        return required_skills
    owner_id = UserSerializer(read_only=True)
    class Meta:
        model = Project
        fields = [
            'id',
            'owner_id',
            'project_name',
            'project_description',
            'created_at',
            'updated_at',
            'suggested_budget',
            'project_state',
            'expected_deadline',
            'skills',       
            'skills_ids',  
            'required_skills'
        ]
    def get_required_skills(self, obj):
        # Return list of skill names for each skill related to the project
        return [skill.skill for skill in obj.skills.all()]

    def validate_expected_deadline(self, value):
        # Validate that the expected deadline is positive and not more than 100 days
        if value <= 0:
            raise serializers.ValidationError("Expected deadline must be a positive number.")
        if value > 100:
            raise serializers.ValidationError("Expected deadline cannot be more than 100 days.")
        return value

    def validate_suggested_budget(self, value):
        # Validate that the suggested budget is positive
        if value <= 0:
            raise serializers.ValidationError("Suggested budget must be a positive number.")
        return value

    def create(self, validated_data):
        # Pop out skills_ids for many-to-many relationship handling
        skills_data = validated_data.pop('skills_ids', [])
        project = Project.objects.create(**validated_data)
        project.skills.set(skills_data)
        return project

    def update(self, instance, validated_data):
        # Pop out skills_ids if provided and update many-to-many relationship
        skills_data = validated_data.pop('skills_ids', None)
        instance = super().update(instance, validated_data)
        if skills_data is not None:
            instance.skills.set(skills_data)
        return instance

class ProposalSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    project = ProjectSerializer(read_only=True)

    class Meta:
        model = Proposal
        fields = '__all__'
        read_only_fields = (
            'id',
            'created_at',
            'updated_at',
            'user',
        )

    def validate_price(self, value):
        if value <= 0:
            serializers.ValidationError("Price must be greater than zero")
        return value
    
    def validate_deadline(self, value):
        if value <= 0:
            serializers.ValidationError("Deadline must be greater than zero days")
        return value