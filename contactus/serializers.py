from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view

from rest_framework import serializers
from .models import ContactUs


class ContactUsSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(
        choices=ContactUs.ContactStatus.choices, default=ContactUs.ContactStatus.PENDING)

    class Meta:
        model = ContactUs
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
