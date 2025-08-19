# Modelos de Gerenciamento de VMs - AnalyticLens

Este documento descreve os modelos Django criados para gerenciar máquinas virtuais de visão computacional.

## Visão Geral

O sistema de gerenciamento de VMs foi projetado para:
- Gerenciar múltiplas máquinas virtuais de visão computacional
- Controlar status, configurações e monitoramento
- Rastrear ferramentas de inspeção e heartbeats
- Integrar com o sistema existente de VMs Flask

## Modelos Principais

### 1. VirtualMachine

Modelo principal para gerenciar uma máquina virtual de visão computacional.

#### Campos Principais

**Identificação:**
- `machine_id`: ID único da máquina (ex: "vm_001")
- `name`: Nome amigável da VM
- `description`: Descrição detalhada
- `owner`: Usuário proprietário da VM

**Status e Operação:**
- `status`: Status atual (stopped, running, error, maintenance, offline)
- `mode`: Modo de operação (PRODUCAO, TESTE, DESENVOLVIMENTO)
- `connection_status`: Status da conexão com o Django
- `is_active`: Se a VM está ativa no sistema

**Configuração de Rede:**
- `django_url`: URL do servidor Django
- `ip_address`: Endereço IP da VM
- `port`: Porta de comunicação

**Configuração de Fonte de Imagem:**
- `source_type`: Tipo de fonte (camera, camera_IP, pasta, rtsp)
- `camera_id`: ID da câmera local
- `resolution_width/height`: Resolução da imagem
- `fps`: Frames por segundo
- `folder_path`: Caminho para pasta de imagens
- `rtsp_url`: URL para stream RTSP

**Configuração de Trigger:**
- `trigger_type`: Tipo de trigger (continuous, manual, external, scheduled)
- `trigger_interval_ms`: Intervalo em milissegundos

**Configuração de Inspeção:**
- `inspection_config`: JSON com configurações de inspeção

**Metadados:**
- `created_at`: Data de criação
- `updated_at`: Data da última atualização
- `last_heartbeat`: Último heartbeat recebido
- `error_message`: Mensagem de erro atual

#### Métodos Úteis

```python
# Verificar status
vm.is_connected()      # True se conectado
vm.is_running()        # True se rodando
vm.can_start()         # True se pode iniciar
vm.can_stop()          # True se pode parar
vm.can_restart()       # True se pode reiniciar

# Obter configurações
vm.get_resolution_display()    # "752x480"
vm.get_source_config()         # Dict com config de fonte
vm.get_trigger_config()        # Dict com config de trigger
vm.get_full_config()           # Configuração completa
```

### 2. VMInspectionTool

Modelo para gerenciar ferramentas de inspeção individuais de uma VM.

#### Campos Principais

**Identificação:**
- `name`: Nome da ferramenta
- `tool_type`: Tipo (grayscale, blob, math, custom)
- `method`: Método de inspeção (luminance, threshold, edge_detection, pattern_matching)

**Configuração:**
- `tool_config`: JSON com configurações específicas da ferramenta
- `roi_config`: JSON com configuração da região de interesse (ROI)
- `inspec_pass_fail`: Se deve fazer teste pass/fail
- `normalize`: Se deve normalizar os resultados

**Relacionamentos:**
- `virtual_machine`: VM à qual a ferramenta pertence

#### Métodos Úteis

```python
# Obter ROI formatado
tool.get_roi_display()  # "(0, 0) - 752x480"
```

### 3. VMHeartbeat

Modelo para registrar heartbeats e monitoramento das VMs.

#### Campos Principais

- `virtual_machine`: VM que enviou o heartbeat
- `timestamp`: Momento do heartbeat
- `status`: Status da VM no momento
- `connection_status`: Status da conexão
- `error_message`: Mensagem de erro se houver
- `performance_metrics`: JSON com métricas de performance

## Uso no Admin Django

Todos os modelos estão registrados no admin com interfaces personalizadas:

### VirtualMachineAdmin
- Lista organizada por status, modo e tipo de fonte
- Filtros por status, modo, conexão e tipo de fonte
- Busca por ID, nome, descrição e IP
- Campos organizados em seções lógicas
- `machine_id` é somente leitura após criação

### VMInspectionToolAdmin
- Lista organizada por tipo de ferramenta e método
- Filtros por tipo, método e status
- Busca por nome da ferramenta e VM

### VMHeartbeatAdmin
- Lista organizada por timestamp
- Filtros por status e conexão
- Hierarquia de datas para navegação
- Não permite criação manual (só automática)

## Exemplos de Uso

### Criar uma nova VM

```python
from api.models import VirtualMachine
from user.models import User

# Criar VM
vm = VirtualMachine.objects.create(
    machine_id="vm_002",
    name="VM de Teste 2",
    description="Segunda VM para testes",
    owner=User.objects.first(),
    django_url="http://localhost:8000",
    source_type="camera",
    camera_id=1,
    resolution_width=640,
    resolution_height=480,
    fps=30,
    trigger_type="continuous",
    trigger_interval_ms=500
)
```

### Adicionar ferramenta de inspeção

```python
from api.models import VMInspectionTool

tool = VMInspectionTool.objects.create(
    name="Filtro Grayscale",
    tool_type="grayscale",
    method="luminance",
    virtual_machine=vm,
    roi_config={
        "x": 0, "y": 0, "w": 640, "h": 480
    },
    tool_config={
        "threshold": 128,
        "normalize": False
    }
)
```

### Registrar heartbeat

```python
from api.models import VMHeartbeat

heartbeat = VMHeartbeat.objects.create(
    virtual_machine=vm,
    status="running",
    connection_status="connected",
    performance_metrics={
        "cpu_usage": 45.2,
        "memory_usage": 67.8,
        "fps_current": 28
    }
)
```

## Integração com VMs Flask

Os modelos foram projetados para integrar com o sistema existente:

1. **Configuração**: O método `get_full_config()` retorna a configuração no formato esperado pelas VMs Flask
2. **Monitoramento**: Heartbeats permitem rastrear status em tempo real
3. **Ferramentas**: Ferramentas de inspeção são mapeadas para o sistema de tools existente
4. **Status**: Estados são sincronizados entre Django e VMs Flask

## Próximos Passos

1. Criar views e serializers para API REST
2. Implementar sistema de comunicação com VMs Flask
3. Criar interface de usuário para gerenciamento
4. Implementar sistema de notificações e alertas
5. Adicionar logs e auditoria
