from django.contrib import admin
from .models import (
    VirtualMachine,
    Inspection,
    InspectionTool,
    ToolKind,
    GrayscaleTool,
    BlurTool,
    ThresholdTool,
    MorphologyTool,
    BlobToolConfig,
    MathTool,
    InspectionResult,
)


@admin.register(VirtualMachine)
class VirtualMachineAdmin(admin.ModelAdmin):
    """Admin para o modelo VirtualMachine"""
    
    list_display = [
        'machine_id', 'name', 'status', 'mode', 'connection_status',
        'ip_address', 'port', 'source_type', 'logs_count', 'logging_buffer_size', 'created_at'
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
        ('Logging (espelhado da VM)', {
            'fields': [
                'logging_enabled', 'logging_mode', 'logging_policy',
                'logging_max_logs', 'logging_batch_size', 'logging_batch_ms',
                'logs_count', 'logging_buffer_size'
            ],
            'classes': ['collapse']
        }),
        ('Metadados', {
            'fields': ['owner', 'created_at', 'updated_at', 'last_heartbeat'],
            'classes': ['collapse']
        })
    ]
    
    ordering = ['-created_at']
    list_per_page = 25


@admin.register(ToolKind)
class ToolKindAdmin(admin.ModelAdmin):
    list_display = ['slug', 'label', 'category', 'updated_at']
    list_filter = ['category']
    search_fields = ['slug', 'label', 'description']
    ordering = ['slug']


class GrayscaleToolInline(admin.StackedInline):
    model = GrayscaleTool
    extra = 0
    can_delete = True


class BlurToolInline(admin.StackedInline):
    model = BlurTool
    extra = 0
    can_delete = True


class ThresholdToolInline(admin.StackedInline):
    model = ThresholdTool
    extra = 0
    can_delete = True


class MorphologyToolInline(admin.StackedInline):
    model = MorphologyTool
    extra = 0
    can_delete = True


class BlobToolConfigInline(admin.StackedInline):
    model = BlobToolConfig
    extra = 0
    can_delete = True


class MathToolInline(admin.StackedInline):
    model = MathTool
    fk_name = 'tool'
    extra = 0
    can_delete = True
    raw_id_fields = ['reference_tool']


@admin.register(InspectionTool)
class InspectionToolAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'tool_kind', 'inspection', 'order_index', 'inspec_pass_fail', 'updated_at']
    list_filter = ['type', 'tool_kind', 'inspec_pass_fail', 'inspection']
    search_fields = ['name']
    raw_id_fields = ['inspection', 'tool_kind']
    inlines = [
        GrayscaleToolInline,
        BlurToolInline,
        ThresholdToolInline,
        MorphologyToolInline,
        BlobToolConfigInline,
        MathToolInline,
    ]
    ordering = ['inspection', 'order_index']


class InspectionToolInline(admin.TabularInline):
    model = InspectionTool
    fields = ['name', 'type', 'tool_kind', 'order_index', 'inspec_pass_fail']
    extra = 0
    show_change_link = True


@admin.register(Inspection)
class InspectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'vm', 'created_at', 'updated_at']
    list_filter = ['vm']
    search_fields = ['name', 'vm__machine_id']
    raw_id_fields = ['vm']
    inlines = [InspectionToolInline]
    ordering = ['vm', 'id']


@admin.register(InspectionResult)
class InspectionResultAdmin(admin.ModelAdmin):
    list_display = ['vm', 'timestamp', 'frame', 'approved', 'reprovadas', 'duration_ms', 'image_url']
    list_filter = ['approved', 'vm']
    search_fields = ['vm__name', 'vm__machine_id', 'cycle_id']
    readonly_fields = ['created_at']
    ordering = ['-timestamp']
