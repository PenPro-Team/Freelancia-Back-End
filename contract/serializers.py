from rest_framework import serializers
from .models import Contract
from freelancia_back_end.models import User, Project
from freelancia_back_end.serializers import UserSerializer as BaseUserSerializer
from freelancia_back_end.serializers import ProjectSerializer as BaseProjectSerializer



class ProjectSerializer(BaseProjectSerializer):
    class Meta:
        model = Project
        fields = (
            'id',
            'project_name',
            'project_description',
            'suggested_budget',
            'expected_deadline',
            'project_state',
        )



class UserSerializer(BaseUserSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name','image')


class ContractSerializer(serializers.ModelSerializer):
    freelancer_details=UserSerializer(source='freelancer' ,read_only=True)
    client_details=UserSerializer(source='client' ,read_only=True)
    project_details = ProjectSerializer(source='project', read_only=True)

    freelancer = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True
    )
    client = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True
    )
    project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(), write_only=True
    )
    class Meta:
        model = Contract
        fields = (
            'id',
            'contract_terms',
            'dedline',
            'budget',
            'freelancer_details',
            'client_details',
            'project_details',
            'freelancer',
            'client',
            'project',
            'created_at',
            'contract_state',
        )
        read_only_fields = (
            'freelancer_details',
            'client_details',
            'project_details',
        )
        