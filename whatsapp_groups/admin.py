from django.contrib import admin
from whatsapp_groups.models import WhatsAppGroup


@admin.register(WhatsAppGroup)
class WhatsAppGroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'subject', 'group_id', 'status', 'business_phone_number', 'created_at']
    list_filter = ['status', 'join_approval_mode', 'created_at']
    search_fields = ['subject', 'group_id', 'business_phone_number']
    readonly_fields = ['group_id', 'invite_link', 'status', 'error_message', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('subject', 'description', 'join_approval_mode')
        }),
        ('WhatsApp API Data', {
            'fields': ('group_id', 'invite_link', 'business_phone_number')
        }),
        ('Status', {
            'fields': ('status', 'error_message')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

