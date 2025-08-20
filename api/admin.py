from django.contrib import admin
from .models import VirtualMachine


@admin.register(VirtualMachine)
class VirtualMachineAdmin(admin.ModelAdmin):
    """Admin para o modelo VirtualMachine"""
    
    list_display = [
        'machine_id', 'name', 'status', 'mode', 'connection_status',
        'ip_address', 'port', 'source_type', 'created_at'
    ]
    
    list_filter = [
        'status', 'mode', 'connection_status', 'source_type',
        'is_active', 'created_at'
    ]
    
    search_fields = [
        'machine_id', 'name', 'description', 'ip_address'
    ]
    
    readonly_fields = [
        'created_at', 'updated_at', 'last_heartbeat'
    ]
    
    fieldsets = [
        ('Identificação', {
            'fields': ['machine_id', 'name', 'description']
        }),
        ('Status', {
            'fields': ['status', 'mode', 'connection_status', 'is_active']
        }),
        ('Rede', {
            'fields': ['django_url', 'ip_address', 'port']
        }),
        ('Fonte', {
            'fields': ['source_type', 'camera_id', 'resolution_width', 'resolution_height', 'fps', 'folder_path', 'rtsp_url']
        }),
        ('Trigger', {
            'fields': ['trigger_type', 'trigger_interval_ms']
        }),
        ('Configuração', {
            'fields': ['inspection_config', 'error_message']
        }),
        ('Metadados', {
            'fields': ['owner', 'created_at', 'updated_at', 'last_heartbeat'],
            'classes': ['collapse']
        })
    ]
    
    ordering = ['-created_at']
    list_per_page = 25
