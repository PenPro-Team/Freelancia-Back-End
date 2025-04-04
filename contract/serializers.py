from rest_framework import serializers
from .models import Contract, Attachment
from freelancia_back_end.models import User, Project
from freelancia_back_end.serializers import UserSerializer as BaseUserSerializer
from freelancia_back_end.serializers import ProjectSerializer as BaseProjectSerializer
from urllib.parse import urljoin
from django.conf import settings



class AttachmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Attachment
        fields = []
    def to_representation(self, instance):
        if instance.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(instance.file.url)
            else:
                return urljoin(settings.MEDIA_URL, str(instance.file))
        return None

   
    

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
    image = serializers.SerializerMethodField()
    def get_image(self, obj):
       return super().get_image(obj)
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name','image')


class ContractSerializer(serializers.ModelSerializer):
    attachments = AttachmentSerializer(many=True)
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
            'attachments',
        )
        read_only_fields = (
            'freelancer_details',
            'client_details',
            'project_details',
        )

    def create(self,valedated_data):
        contract= super().create(valedated_data)

        project= contract.project
        project.project_state=project.StatusChoices.ongoing 
        project.save()
        return contract
    
    def update(self,instance,valedated_data):
        previous_state=instance.contract_state
        contract= super().update(instance,valedated_data)
        new_state=contract.contract_state

        if previous_state != new_state:
            project= contract.project
            if new_state=='canceled':
                project.project_state=project.StatusChoices.contract_canceled_and_reopened
            elif new_state=='finished':
                project.project_state=project.StatusChoices.finished
            project.save()
        return contract
        