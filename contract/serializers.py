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
        representation={}
        if instance.file:
            request = self.context.get('request')
            if request:
                representation['file'] = urljoin(request.build_absolute_uri(), str(instance.file))
            else:
               representation['file'] =  urljoin(settings.MEDIA_URL, str(instance.file))
        else:
            representation['file'] = None
        
        if instance.description:
            representation['description'] = instance.description

        return representation
   
    

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
    attachments = serializers.SerializerMethodField(required=False)
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
            'deadline',
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
        project.project_state=Project.StatusChoices.ongoing 
        project.save()
        return contract
    
    def update(self,instance,valedated_data):
        previous_state=instance.contract_state
        contract= super().update(instance,valedated_data)
        new_state=contract.contract_state

        if previous_state != new_state:
            project= contract.project
            if new_state==Contract.StatusChoices.canceled:
                project.project_state=Project.StatusChoices.contract_canceled_and_reopened
            elif new_state==Contract.StatusChoices.completed:
                project.project_state=Project.StatusChoices.finished
            project.save()
        return contract

    def get_attachments(self, obj):
   
        attachments = obj.attachments.all()
        
        # If no attachments, return empty result
        if not attachments.exists():
            return {}
        
        # Get unique descriptions
        descriptions = attachments.exclude(description__isnull=True).exclude(description='').values_list('description', flat=True).distinct()
        
        # Use the first description if any exists
        description = descriptions.first() if descriptions else ""
        
        # Get all file URLs
        files = []
        for attachment in attachments:
            if attachment.file:
                request = self.context.get('request')
                if request:
                    file_url = request.build_absolute_uri(attachment.file.url)
                else:
                    file_url = urljoin(settings.MEDIA_URL, str(attachment.file))
                files.append(file_url)
        
        # Return in desired format
        return {
            'description': description,
            'files': files
        }
