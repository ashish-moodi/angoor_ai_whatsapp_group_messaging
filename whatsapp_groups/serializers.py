from rest_framework import serializers
from whatsapp_groups.models import WhatsAppGroup


class WhatsAppGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhatsAppGroup
        fields = '__all__'
        read_only_fields = ['id', 'group_id', 'request_id', 'invite_link', 'status', 'error_message', 'created_at', 'updated_at']


class CreateGroupRequestSerializer(serializers.Serializer):
    subject = serializers.CharField(
        max_length=128,
        required=True,
        help_text="Group subject (max 128 characters)"
    )
    description = serializers.CharField(
        max_length=2048,
        required=False,
        allow_blank=True,
        help_text="Group description (max 2048 characters)"
    )
    join_approval_mode = serializers.ChoiceField(
        choices=WhatsAppGroup.JoinApprovalMode.choices,
        default=WhatsAppGroup.JoinApprovalMode.AUTO_APPROVE,
        required=False,
        help_text="Join approval mode: 'approval_required' or 'auto_approve'"
    )
    
    def validate_subject(self, value):
        """Trim whitespace from subject."""
        return value.strip() if value else value

