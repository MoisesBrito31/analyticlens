from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class VirtualMachine(models.Model):
    """
    Modelo simplificado para máquinas de visão
    Apenas estrutura de dados básica - funcionalidades serão implementadas depois
    """
    
    # Status básicos
    STATUS_CHOICES = [
        ('running', 'Rodando'),
        ('stopped', 'Parada'),
        ('error', 'Erro'),
        ('offline', 'Offline'),
    ]
    
    # Modos básicos
    MODE_CHOICES = [
        ('TESTE', 'Teste'),
        ('PRODUCAO', 'Produção'),
    ]
    
    # Status de conexão básico
    CONNECTION_STATUS_CHOICES = [
        ('connected', 'Conectada'),
        ('disconnected', 'Desconectada'),
    ]
    
    # Tipo de fonte básico
    SOURCE_TYPE_CHOICES = [
        ('camera', 'Câmera'),
        ('pasta', 'Pasta de Imagens'),
        ('rtsp', 'Stream RTSP'),
    ]
    
    # Tipo de trigger básico
    TRIGGER_TYPE_CHOICES = [
        ('continuous', 'Contínuo'),
        ('manual', 'Manual'),
        ('interval', 'Intervalo'),
    ]
    
    # Campos básicos de identificação
    machine_id = models.CharField(max_length=50, unique=True, verbose_name="ID da Máquina")
    name = models.CharField(max_length=100, verbose_name="Nome da VM")
    description = models.TextField(blank=True, verbose_name="Descrição")
    
    # Campos básicos de status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='stopped', verbose_name="Status")
    mode = models.CharField(max_length=20, choices=MODE_CHOICES, default='TESTE', verbose_name="Modo de Operação")
    connection_status = models.CharField(max_length=20, choices=CONNECTION_STATUS_CHOICES, default='disconnected', verbose_name="Status da Conexão")
    
    # Campos básicos de rede
    django_url = models.CharField(max_length=500, blank=True, verbose_name="URL do Django")
    ip_address = models.CharField(max_length=45, blank=True, null=True, verbose_name="Endereço IP")
    port = models.IntegerField(default=5000, validators=[MinValueValidator(1), MaxValueValidator(65535)], verbose_name="Porta")
    
    # Campos básicos de fonte
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPE_CHOICES, default='camera', verbose_name="Tipo de Fonte")
    camera_id = models.IntegerField(default=0, verbose_name="ID da Câmera")
    resolution_width = models.IntegerField(default=752, verbose_name="Largura da Resolução")
    resolution_height = models.IntegerField(default=480, verbose_name="Altura da Resolução")
    fps = models.IntegerField(default=30, validators=[MinValueValidator(1), MaxValueValidator(120)], verbose_name="FPS")
    folder_path = models.CharField(max_length=500, blank=True, verbose_name="Caminho da Pasta")
    rtsp_url = models.CharField(max_length=500, blank=True, verbose_name="URL RTSP")
    
    # Campos básicos de trigger
    trigger_type = models.CharField(max_length=20, choices=TRIGGER_TYPE_CHOICES, default='continuous', verbose_name="Tipo de Trigger")
    trigger_interval_ms = models.IntegerField(default=1000, validators=[MinValueValidator(100)], verbose_name="Intervalo do Trigger (ms)")
    
    # Campos básicos de configuração
    inspection_config = models.JSONField(default=dict, verbose_name="Configuração de Inspeção")
    
    # Metadados básicos
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    last_heartbeat = models.DateTimeField(blank=True, null=True, verbose_name="Último Heartbeat")
    error_message = models.TextField(blank=True, verbose_name="Mensagem de Erro")
    
    # Relacionamentos básicos
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Proprietário")
    is_active = models.BooleanField(default=True, verbose_name="Ativa")
    
    class Meta:
        verbose_name = "Máquina Virtual"
        verbose_name_plural = "Máquinas Virtuais"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.machine_id})"
    
    def get_resolution_display(self):
        """Retorna a resolução formatada"""
        return f"{self.resolution_width}x{self.resolution_height}"
