from rest_framework import serializers
from .models import ReportUser, ReportContract
from freelancia_back_end.models import User
from contract.serializers import ContractSerializer
from freelancia_back_end.serializers import PublicUserSerializer

# class PublicUserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ["id", "username", "first_name", "last_name"]


class BaseReportSerializer(serializers.ModelSerializer):
    reporter = PublicUserSerializer(read_only=True)
    resolved_by = PublicUserSerializer(read_only=True)
    title = serializers.CharField(max_length=255, allow_blank=False)
    description = serializers.CharField(allow_blank=False)

    class Meta:
        fields = [
            "id", "title", "description", "status",
            "resolved_notes", "resolution_reason",
            "resolved_by", "resolved_at",
            "created_at", "updated_at", "reporter"
        ]
        read_only_fields = [
            "id", "created_at", "updated_at",
            "resolved_at", "resolved_by"
        ]

    def validate_status(self, value):
        if value not in self.Meta.model.StatusChoices.values:
            raise serializers.ValidationError("Invalid status choice.")
        return value

    def validate_resolution_reason(self, value):
        if value and value not in self.Meta.model.ResolutionReason.values:
            raise serializers.ValidationError("Invalid resolution reason.")
        return value


class ReportUserSerializer(BaseReportSerializer):
    user = PublicUserSerializer(read_only=True)

    class Meta(BaseReportSerializer.Meta):
        model = ReportUser
        fields = BaseReportSerializer.Meta.fields + ["user"]
        extra_kwargs = {
            "user": {"read_only": True},
        }


class ReportContractSerializer(BaseReportSerializer):
    contract = ContractSerializer(read_only=True)

    class Meta(BaseReportSerializer.Meta):
        model = ReportContract
        fields = BaseReportSerializer.Meta.fields + ["contract"]
        extra_kwargs = {
            "contract": {"read_only": True},
        }


class CreateReportUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportUser
        fields = ["user", "title", "description"]


class CreateReportContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportContract
        fields = ["contract", "title", "description"]


class UpdateReportStatusSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ["status", "resolved_notes", "resolution_reason"]
        abstract = True

    def update(self, instance, validated_data):
        if validated_data.get('status') in ['resolved', 'ignored']:
            validated_data['resolved_by'] = self.context['request'].user
        return super().update(instance, validated_data)


class UpdateUserReportStatusSerializer(UpdateReportStatusSerializer):
    class Meta(UpdateReportStatusSerializer.Meta):
        model = ReportUser


class UpdateContractReportStatusSerializer(UpdateReportStatusSerializer):
    class Meta(UpdateReportStatusSerializer.Meta):
        model = ReportContract
