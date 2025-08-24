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


class Inspection(models.Model):
    """Inspeção executada/definida para uma VM."""

    vm = models.ForeignKey(
        VirtualMachine,
        on_delete=models.CASCADE,
        related_name='inspections',
        verbose_name='Máquina'
    )
    name = models.CharField(max_length=100, verbose_name='Nome da Inspeção')
    description = models.TextField(blank=True, verbose_name='Descrição')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        verbose_name = 'Inspeção'
        verbose_name_plural = 'Inspeções'
        ordering = ['vm_id', 'id']


class ToolKind(models.Model):
    """Catálogo de tipos de ferramentas (extensível via dados)."""

    CATEGORY_CHOICES = [
        ('filter', 'Filtro'),
        ('analytic', 'Analítica'),
        ('math', 'Matemática'),
    ]

    slug = models.SlugField(max_length=50, unique=True, verbose_name='Slug')
    label = models.CharField(max_length=100, verbose_name='Rótulo')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name='Categoria')
    description = models.TextField(blank=True, verbose_name='Descrição')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tipo de Tool'
        verbose_name_plural = 'Tipos de Tools'
        ordering = ['slug']

class InspectionTool(models.Model):
    """Ferramenta base: apenas campos comuns; configs ficam nos modelos específicos por tipo."""

    TOOL_TYPE_CHOICES = [
        ('grayscale', 'Grayscale'),
        ('blur', 'Blur'),
        ('threshold', 'Threshold'),
        ('morphology', 'Morphology'),
        ('blob', 'Blob'),
        ('math', 'Math'),
    ]

    inspection = models.ForeignKey(
        Inspection,
        on_delete=models.CASCADE,
        related_name='tools',
        verbose_name='Inspeção'
    )
    order_index = models.PositiveIntegerField(default=0, verbose_name='Ordem no Pipeline')
    name = models.CharField(max_length=100, verbose_name='Nome da Tool')
    type = models.CharField(max_length=20, choices=TOOL_TYPE_CHOICES, verbose_name='Tipo')
    tool_kind = models.ForeignKey(
        ToolKind,
        on_delete=models.PROTECT,
        related_name='inspection_tools',
        verbose_name='Tipo (ToolKind)',
        null=True,
        blank=True
    )

    roi_x = models.IntegerField(default=0, verbose_name='ROI X')
    roi_y = models.IntegerField(default=0, verbose_name='ROI Y')
    roi_w = models.IntegerField(default=0, verbose_name='ROI Largura')
    roi_h = models.IntegerField(default=0, verbose_name='ROI Altura')

    inspec_pass_fail = models.BooleanField(default=False, verbose_name='Afeta Pass/Fail')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Ferramenta de Inspeção'
        verbose_name_plural = 'Ferramentas de Inspeção'
        ordering = ['inspection_id', 'order_index', 'id']


class GrayscaleTool(models.Model):
    tool = models.OneToOneField(InspectionTool, on_delete=models.CASCADE, related_name='grayscale')
    method = models.CharField(
        max_length=20,
        choices=[('luminance', 'Luminance'), ('average', 'Average'), ('weighted', 'Weighted')],
        default='luminance'
    )
    normalize = models.BooleanField(default=False)


class BlurTool(models.Model):
    tool = models.OneToOneField(InspectionTool, on_delete=models.CASCADE, related_name='blur')
    method = models.CharField(
        max_length=20,
        choices=[('gaussian', 'Gaussian'), ('median', 'Median')],
        default='gaussian'
    )
    ksize = models.IntegerField(default=3, validators=[MinValueValidator(1)])
    sigma = models.FloatField(default=0.0)


class ThresholdTool(models.Model):
    tool = models.OneToOneField(InspectionTool, on_delete=models.CASCADE, related_name='threshold')
    mode = models.CharField(
        max_length=20,
        choices=[('binary', 'Binary'), ('range', 'Range'), ('otsu', 'Otsu')],
        default='binary'
    )
    th_min = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(255)])
    th_max = models.IntegerField(default=255, validators=[MinValueValidator(0), MaxValueValidator(255)])


class MorphologyTool(models.Model):
    tool = models.OneToOneField(InspectionTool, on_delete=models.CASCADE, related_name='morphology')
    kernel = models.IntegerField(default=3, validators=[MinValueValidator(1)])
    open = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    close = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    shape = models.CharField(
        max_length=20,
        choices=[('ellipse', 'Ellipse'), ('rect', 'Rect'), ('cross', 'Cross')],
        default='ellipse'
    )


class BlobToolConfig(models.Model):
    tool = models.OneToOneField(InspectionTool, on_delete=models.CASCADE, related_name='blob')
    th_min = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(255)])
    th_max = models.IntegerField(default=255, validators=[MinValueValidator(0), MaxValueValidator(255)])
    area_min = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)])
    area_max = models.FloatField(default=1e12, validators=[MinValueValidator(0.0)])
    total_area_test = models.BooleanField(default=False)
    blob_count_test = models.BooleanField(default=False)
    test_total_area_min = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)])
    test_total_area_max = models.FloatField(default=1e12, validators=[MinValueValidator(0.0)])
    test_blob_count_min = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    test_blob_count_max = models.IntegerField(default=1_000_000, validators=[MinValueValidator(0)])
    contour_chain = models.CharField(
        max_length=20,
        choices=[('SIMPLE', 'SIMPLE'), ('NONE', 'NONE'), ('TC89_L1', 'TC89_L1'), ('TC89_KCOS', 'TC89_KCOS')],
        default='SIMPLE'
    )
    approx_epsilon_ratio = models.FloatField(default=0.01, validators=[MinValueValidator(0.0)])
    polygon_max_points = models.IntegerField(default=0, validators=[MinValueValidator(0)])


class MathTool(models.Model):
    tool = models.OneToOneField(InspectionTool, on_delete=models.CASCADE, related_name='math')
    operation = models.CharField(
        max_length=30,
        choices=[('area_ratio', 'Area Ratio'), ('blob_density', 'Blob Density'), ('custom_formula', 'Custom Formula')],
        blank=True
    )
    reference_tool = models.ForeignKey(InspectionTool, null=True, blank=True, on_delete=models.SET_NULL, related_name='referenced_by_math')
    custom_formula = models.TextField(blank=True)
