from django.contrib import admin
from .models import VirtualMachine, VMInspectionTool, VMHeartbeat

@admin.register(VirtualMachine)
class VirtualMachineAdmin(admin.ModelAdmin):
    list_display = ['machine_id', 'name', 'status', 'mode', 'connection_status', 'source_type', 'owner', 'is_active', 'created_at']
    list_filter = ['status', 'mode', 'connection_status', 'source_type', 'is_active', 'created_at']
    search_fields = ['machine_id', 'name', 'description', 'ip_address']
    readonly_fields = ['created_at', 'updated_at', 'last_heartbeat']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('machine_id', 'name', 'description', 'owner', 'is_active')
        }),
        ('Status e Configuração', {
            'fields': ('status', 'mode', 'connection_status', 'error_message')
        }),
        ('Configuração de Rede', {
            'fields': ('django_url', 'ip_address', 'port')
        }),
        ('Configuração de Fonte', {
            'fields': ('source_type', 'camera_id', 'resolution_width', 'resolution_height', 'fps', 'folder_path', 'rtsp_url')
        }),
        ('Configuração de Trigger', {
            'fields': ('trigger_type', 'trigger_interval_ms')
        }),
        ('Configuração de Inspeção', {
            'fields': ('inspection_config',)
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at', 'last_heartbeat'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('owner')
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editando um objeto existente
            return self.readonly_fields + ('machine_id',)
        return self.readonly_fields

@admin.register(VMInspectionTool)
class VMInspectionToolAdmin(admin.ModelAdmin):
    list_display = ['name', 'tool_type', 'method', 'virtual_machine', 'inspec_pass_fail', 'is_active', 'created_at']
    list_filter = ['tool_type', 'method', 'inspec_pass_fail', 'is_active', 'created_at']
    search_fields = ['name', 'virtual_machine__name', 'virtual_machine__machine_id']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('name', 'tool_type', 'method', 'virtual_machine', 'is_active')
        }),
        ('Configuração', {
            'fields': ('tool_config', 'roi_config')
        }),
        ('Parâmetros de Teste', {
            'fields': ('inspec_pass_fail', 'normalize')
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('virtual_machine')

@admin.register(VMHeartbeat)
class VMHeartbeatAdmin(admin.ModelAdmin):
    list_display = ['virtual_machine', 'timestamp', 'status', 'connection_status', 'has_error']
    list_filter = ['status', 'connection_status', 'timestamp']
    search_fields = ['virtual_machine__name', 'virtual_machine__machine_id', 'error_message']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Informações da VM', {
            'fields': ('virtual_machine', 'timestamp')
        }),
        ('Status', {
            'fields': ('status', 'connection_status')
        }),
        ('Detalhes', {
            'fields': ('error_message', 'performance_metrics')
        }),
    )
    
    def has_error(self, obj):
        return bool(obj.error_message)
    has_error.boolean = True
    has_error.short_description = 'Tem Erro'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('virtual_machine')
    
    def has_add_permission(self, request):
        # Heartbeats são criados automaticamente, não devem ser criados manualmente
        return False
