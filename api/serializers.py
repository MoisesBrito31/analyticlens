from rest_framework import serializers
from .models import VirtualMachine


class VirtualMachineListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem de VMs"""
    
    resolution = serializers.SerializerMethodField()
    
    class Meta:
        model = VirtualMachine
        fields = [
            'id', 'machine_id', 'name', 'description', 'status', 'mode',
            'connection_status', 'ip_address', 'port', 'source_type',
            'resolution', 'fps', 'trigger_type', 'last_heartbeat',
            'error_message', 'created_at', 'updated_at'
        ]
    
    def get_resolution(self, obj):
        """Retorna a resolução formatada de forma segura"""
        try:
            if hasattr(obj, 'resolution_width') and hasattr(obj, 'resolution_height'):
                width = getattr(obj, 'resolution_width', 0)
                height = getattr(obj, 'resolution_height', 0)
                return f"{width}x{height}"
            else:
                return "N/A"
        except Exception as e:
            return "Erro"


class VirtualMachineSerializer(serializers.ModelSerializer):
    """Serializer completo para VMs (detalhes)"""
    
    resolution = serializers.SerializerMethodField()
    
    class Meta:
        model = VirtualMachine
        fields = [
            'id', 'machine_id', 'name', 'description', 'status', 'mode',
            'connection_status', 'django_url', 'ip_address', 'port',
            'source_type', 'camera_id', 'resolution_width', 'resolution_height',
            'fps', 'folder_path', 'rtsp_url', 'trigger_type', 'trigger_interval_ms',
            'inspection_config', 'last_heartbeat', 'error_message', 'created_at',
            'updated_at', 'resolution'
        ]
    
    def get_resolution(self, obj):
        """Retorna a resolução formatada de forma segura"""
        try:
            if hasattr(obj, 'resolution_width') and hasattr(obj, 'resolution_height'):
                width = getattr(obj, 'resolution_width', 0)
                height = getattr(obj, 'resolution_height', 0)
                return f"{width}x{height}"
            else:
                return "N/A"
        except Exception as e:
            return "Erro"


class VirtualMachineCreateSerializer(serializers.ModelSerializer):
    """Serializer para criação de VMs"""
    
    class Meta:
        model = VirtualMachine
        fields = [
            'machine_id', 'name', 'description', 'django_url', 'ip_address',
            'port', 'source_type', 'camera_id', 'resolution_width',
            'resolution_height', 'fps', 'folder_path', 'rtsp_url',
            'trigger_type', 'trigger_interval_ms', 'inspection_config', 'mode'
        ]
    
    def validate_machine_id(self, value):
        """Valida se machine_id é único"""
        if VirtualMachine.objects.filter(machine_id=value).exists():
            raise serializers.ValidationError("Machine ID já existe")
        return value


class VirtualMachineUpdateSerializer(serializers.ModelSerializer):
    """Serializer para atualização de VMs"""
    
    class Meta:
        model = VirtualMachine
        fields = [
            'name', 'description', 'django_url', 'ip_address', 'port',
            'source_type', 'camera_id', 'resolution_width', 'resolution_height',
            'fps', 'folder_path', 'rtsp_url', 'trigger_type', 'trigger_interval_ms',
            'inspection_config', 'mode'
        ]


class VMActionSerializer(serializers.Serializer):
    """Serializer para ações da VM"""
    ACTION_CHOICES = [
        ('start', 'Iniciar'),
        ('stop', 'Parar'),
        ('restart', 'Reiniciar'),
        ('trigger', 'Trigger Manual')
    ]
    
    action = serializers.ChoiceField(choices=ACTION_CHOICES)


class VMSearchSerializer(serializers.Serializer):
    """Serializer para parâmetros de busca de VMs"""
    status = serializers.ChoiceField(
        choices=VirtualMachine.STATUS_CHOICES,
        required=False, 
        allow_blank=True
    )
    mode = serializers.ChoiceField(
        choices=VirtualMachine.MODE_CHOICES,
        required=False, 
        allow_blank=True
    )
    connection_status = serializers.ChoiceField(
        choices=VirtualMachine.CONNECTION_STATUS_CHOICES,
        required=False, 
        allow_blank=True
    )
    search = serializers.CharField(required=False, allow_blank=True)


class VMStatusSummarySerializer(serializers.Serializer):
    """Serializer para resumo de status das VMs"""
    total_vms = serializers.IntegerField()
    status_counts = serializers.DictField()
    connection_counts = serializers.DictField()
    mode_counts = serializers.DictField()
    error_vms = serializers.ListField()
    offline_vms = serializers.ListField()
    timestamp = serializers.DateTimeField()
