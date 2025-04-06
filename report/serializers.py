from rest_framework import serializers
from .models import ReportUser
from freelancia_back_end.models import User


class PublicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


class ReportUserSerializer(serializers.ModelSerializer):
    user = PublicUserSerializer(read_only=True)
    reporter = PublicUserSerializer(read_only=True)
    title = serializers.CharField(max_length=255, allow_blank=False)
    description = serializers.CharField(allow_blank=False)

    class Meta:
        model = ReportUser
        fields = [
            "id", "user", "reporter", "title", "description",
            "status", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
        extra_kwargs = {
            "user": {"read_only": True},
            "reporter": {"read_only": True},
        }

    def validate_status(self, value):
        if value not in ReportUser.StatusChoices.values:
            raise serializers.ValidationError("Invalid status choice.")
        return value
