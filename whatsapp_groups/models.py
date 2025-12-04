from django.db import models
from django.utils.translation import gettext_lazy as _


class WhatsAppGroup(models.Model):
    class JoinApprovalMode(models.TextChoices):
        APPROVAL_REQUIRED = 'approval_required', _('Approval Required')
        AUTO_APPROVE = 'auto_approve', _('Auto Approve')
    
    # WhatsApp API fields
    group_id = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        help_text=_("WhatsApp Group ID returned from API (received via webhook)")
    )
    request_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text=_("WhatsApp request_id returned from initial API call")
    )
    subject = models.CharField(
        max_length=128,
        help_text=_("Group subject (max 128 characters)")
    )
    description = models.TextField(
        max_length=2048,
        blank=True,
        null=True,
        help_text=_("Group description (max 2048 characters)")
    )
    join_approval_mode = models.CharField(
        max_length=20,
        choices=JoinApprovalMode.choices,
        default=JoinApprovalMode.AUTO_APPROVE,
        help_text=_("Join approval mode for the group")
    )
    invite_link = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text=_("Invite link for the group")
    )
    
    business_phone_number = models.CharField(
        max_length=20,
        help_text=_("Business phone number ID used to create the group")
    )
    
    status = models.CharField(
        max_length=50,
        default='pending',
        help_text=_("Status of group creation")
    )
    error_message = models.TextField(
        blank=True,
        null=True,
        help_text=_("Error message if group creation failed")
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("WhatsApp Group")
        verbose_name_plural = _("WhatsApp Groups")
        indexes = [
            models.Index(fields=['group_id']),
            models.Index(fields=['business_phone_number']),
            models.Index(fields=['status']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.subject} ({self.group_id or 'Pending'})"

