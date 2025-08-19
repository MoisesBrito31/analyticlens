from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
import json

# Create your models here.

class VirtualMachine(models.Model):
    """
    Modelo para gerenciar máquinas virtuais de visão computacional
    """
    
    # Status choices
    STATUS_CHOICES = [
        ('stopped', 'Parada'),
        ('running', 'Executando'),
        ('error', 'Erro'),
        ('maintenance', 'Manutenção'),
        ('offline', 'Offline'),
    ]
    
    MODE_CHOICES = [
        ('PRODUCAO', 'Produção'),
        ('TESTE', 'Teste'),
        ('DESENVOLVIMENTO', 'Desenvolvimento'),
    ]
    
    CONNECTION_STATUS_CHOICES = [
        ('connected', 'Conectado'),
        ('disconnected', 'Desconectado'),
        ('connecting', 'Conectando'),
        ('error', 'Erro de Conexão'),
    ]
    
    SOURCE_TYPE_CHOICES = [
        ('camera', 'Câmera Local'),
        ('camera_IP', 'Câmera IP'),
        ('pasta', 'Pasta de Imagens'),
        ('rtsp', 'Stream RTSP'),
    ]
    
    TRIGGER_TYPE_CHOICES = [
        ('continuous', 'Contínuo'),
        ('manual', 'Manual'),
        ('external', 'Externo'),
        ('scheduled', 'Agendado'),
    ]
    
    # Campos básicos
    machine_id = models.CharField(max_length=50, unique=True, verbose_name="ID da Máquina")
    name = models.CharField(max_length=100, verbose_name="Nome da VM")
    description = models.TextField(blank=True, verbose_name="Descrição")
    
    # Status e configuração
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='stopped', verbose_name="Status")
    mode = models.CharField(max_length=20, choices=MODE_CHOICES, default='TESTE', verbose_name="Modo de Operação")
    connection_status = models.CharField(max_length=20, choices=CONNECTION_STATUS_CHOICES, default='disconnected', verbose_name="Status da Conexão")
    
    # Configuração de rede
    django_url = models.URLField(verbose_name="URL do Django")
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name="Endereço IP")
    port = models.IntegerField(default=5000, validators=[MinValueValidator(1), MaxValueValidator(65535)], verbose_name="Porta")
    
    # Configuração de fonte de imagem
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPE_CHOICES, default='camera', verbose_name="Tipo de Fonte")
    camera_id = models.IntegerField(default=0, verbose_name="ID da Câmera")
    resolution_width = models.IntegerField(default=752, verbose_name="Largura da Resolução")
    resolution_height = models.IntegerField(default=480, verbose_name="Altura da Resolução")
    fps = models.IntegerField(default=30, validators=[MinValueValidator(1), MaxValueValidator(120)], verbose_name="FPS")
    folder_path = models.CharField(max_length=500, blank=True, verbose_name="Caminho da Pasta")
    rtsp_url = models.URLField(blank=True, verbose_name="URL RTSP")
    
    # Configuração de trigger
    trigger_type = models.CharField(max_length=20, choices=TRIGGER_TYPE_CHOICES, default='continuous', verbose_name="Tipo de Trigger")
    trigger_interval_ms = models.IntegerField(default=1000, validators=[MinValueValidator(100)], verbose_name="Intervalo do Trigger (ms)")
    
    # Configuração de inspeção
    inspection_config = models.JSONField(default=dict, verbose_name="Configuração de Inspeção")
    
    # Metadados
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    last_heartbeat = models.DateTimeField(blank=True, null=True, verbose_name="Último Heartbeat")
    error_message = models.TextField(blank=True, verbose_name="Mensagem de Erro")
    
    # Relacionamentos
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Proprietário")
    is_active = models.BooleanField(default=True, verbose_name="Ativa")
    
    class Meta:
        verbose_name = "Máquina Virtual"
        verbose_name_plural = "Máquinas Virtuais"
        ordering = ['-created_at']
        db_table = 'api_virtual_machine'
    
    def __str__(self):
        return f"{self.name} ({self.machine_id})"
    
    def get_resolution_display(self):
        """Retorna a resolução formatada"""
        return f"{self.resolution_width}x{self.resolution_height}"
    
    def get_source_config(self):
        """Retorna a configuração de fonte como dicionário"""
        return {
            'type': self.source_type,
            'camera_id': self.camera_id,
            'resolution': [self.resolution_width, self.resolution_height],
            'fps': self.fps,
            'folder_path': self.folder_path,
            'rtsp_url': self.rtsp_url,
        }
    
    def get_trigger_config(self):
        """Retorna a configuração de trigger como dicionário"""
        return {
            'type': self.trigger_type,
            'interval_ms': self.trigger_interval_ms,
        }
    
    def get_full_config(self):
        """Retorna a configuração completa da VM"""
        return {
            'machine_id': self.machine_id,
            'django_url': self.django_url,
            'status': self.status,
            'mode': self.mode,
            'connection_status': self.connection_status,
            'inspection_config': self.inspection_config,
            'source_config': self.get_source_config(),
            'trigger_config': self.get_trigger_config(),
            'error_msg': self.error_message,
            'last_saved': self.updated_at.isoformat(),
        }
    
    def is_connected(self):
        """Verifica se a VM está conectada"""
        return self.connection_status == 'connected'
    
    def is_running(self):
        """Verifica se a VM está rodando"""
        return self.status == 'running'
    
    def can_start(self):
        """Verifica se a VM pode ser iniciada"""
        return self.status in ['stopped', 'error'] and self.is_connected()
    
    def can_stop(self):
        """Verifica se a VM pode ser parada"""
        return self.status == 'running'
    
    def can_restart(self):
        """Verifica se a VM pode ser reiniciada"""
        return self.status in ['running', 'error'] and self.is_connected()


class VMInspectionTool(models.Model):
    """
    Modelo para gerenciar ferramentas de inspeção das VMs
    """
    
    TOOL_TYPE_CHOICES = [
        ('grayscale', 'Filtro Grayscale'),
        ('blob', 'Detector de Blob'),
        ('math', 'Ferramenta Matemática'),
        ('custom', 'Personalizada'),
    ]
    
    METHOD_CHOICES = [
        ('luminance', 'Luminância'),
        ('threshold', 'Threshold'),
        ('edge_detection', 'Detecção de Bordas'),
        ('pattern_matching', 'Correspondência de Padrões'),
    ]
    
    # Campos básicos
    name = models.CharField(max_length=100, verbose_name="Nome da Ferramenta")
    tool_type = models.CharField(max_length=20, choices=TOOL_TYPE_CHOICES, verbose_name="Tipo de Ferramenta")
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, verbose_name="Método")
    
    # Configuração da ferramenta
    tool_config = models.JSONField(default=dict, verbose_name="Configuração da Ferramenta")
    roi_config = models.JSONField(default=dict, verbose_name="Configuração ROI")
    
    # Parâmetros de teste
    inspec_pass_fail = models.BooleanField(default=True, verbose_name="Teste Pass/Fail")
    normalize = models.BooleanField(default=False, verbose_name="Normalizar")
    
    # Relacionamentos
    virtual_machine = models.ForeignKey(VirtualMachine, on_delete=models.CASCADE, related_name='inspection_tools', verbose_name="Máquina Virtual")
    
    # Metadados
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    is_active = models.BooleanField(default=True, verbose_name="Ativa")
    
    class Meta:
        verbose_name = "Ferramenta de Inspeção"
        verbose_name_plural = "Ferramentas de Inspeção"
        ordering = ['name']
        db_table = 'api_vm_inspection_tool'
    
    def __str__(self):
        return f"{self.name} ({self.get_tool_type_display()})"
    
    def get_roi_display(self):
        """Retorna a configuração ROI formatada"""
        roi = self.roi_config
        if roi:
            return f"({roi.get('x', 0)}, {roi.get('y', 0)}) - {roi.get('w', 0)}x{roi.get('h', 0)}"
        return "Não configurado"


class VMHeartbeat(models.Model):
    """
    Modelo para registrar heartbeats das VMs
    """
    
    virtual_machine = models.ForeignKey(VirtualMachine, on_delete=models.CASCADE, related_name='heartbeats', verbose_name="Máquina Virtual")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Timestamp")
    status = models.CharField(max_length=20, choices=VirtualMachine.STATUS_CHOICES, verbose_name="Status")
    connection_status = models.CharField(max_length=20, choices=VirtualMachine.CONNECTION_STATUS_CHOICES, verbose_name="Status da Conexão")
    error_message = models.TextField(blank=True, verbose_name="Mensagem de Erro")
    performance_metrics = models.JSONField(default=dict, verbose_name="Métricas de Performance")
    
    class Meta:
        verbose_name = "Heartbeat da VM"
        verbose_name_plural = "Heartbeats das VMs"
        ordering = ['-timestamp']
        db_table = 'api_vm_heartbeat'
    
    def __str__(self):
        return f"Heartbeat de {self.virtual_machine.name} em {self.timestamp}"
