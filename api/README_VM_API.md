# Vision Machine (VM) API Documentation

## Visão Geral

Esta API permite gerenciar máquinas virtuais de visão computacional (VMs) no sistema analyticLens. Cada VM pode ter múltiplas ferramentas de inspeção e gera heartbeats para monitoramento.

**Tecnologia:** Django REST Framework (DRF) com autenticação e validação automática.

## Endpoints

### 1. Listar e Criar VMs

#### GET `/api/vms`
Lista todas as VMs com paginação e filtros.

**Parâmetros de Query:**
- `page` (int): Número da página (padrão: 1)
- `per_page` (int): Itens por página (padrão: 10, máximo: 100)
- `status` (string): Filtrar por status (stopped, running, error, maintenance, offline)
- `mode` (string): Filtrar por modo (PRODUCAO, TESTE, DESENVOLVIMENTO)
- `connection_status` (string): Filtrar por status de conexão (connected, disconnected, connecting, error)
- `search` (string): Buscar por nome, machine_id ou descrição

**Exemplo de Resposta:**
```json
{
  "vms": [
    {
      "id": 1,
      "machine_id": "VM001",
      "name": "Câmera Principal",
      "description": "Câmera de inspeção da linha de produção",
      "status": "running",
      "mode": "PRODUCAO",
      "connection_status": "connected",
      "ip_address": "192.168.1.100",
      "port": 5000,
      "source_type": "camera",
      "resolution": "752x480",
      "fps": 30,
      "trigger_type": "continuous",
      "last_heartbeat": "2024-01-15T10:30:00Z",
      "error_message": null,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-15T10:30:00Z",
      "can_start": false,
      "can_stop": true,
      "can_restart": true
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total_pages": 1,
    "total_count": 1,
    "has_next": false,
    "has_previous": false
  }
}
```

#### POST `/api/vms`
Cria uma nova VM.

**Corpo da Requisição:**
```json
{
  "machine_id": "VM002",
  "name": "Câmera Secundária",
  "description": "Câmera de backup",
  "django_url": "http://192.168.1.101:5000",
  "ip_address": "192.168.1.101",
  "port": 5000,
  "source_type": "camera",
  "camera_id": 1,
  "resolution_width": 640,
  "resolution_height": 480,
  "fps": 25,
  "trigger_type": "manual",
  "trigger_interval_ms": 2000
}
```

**Campos Obrigatórios:**
- `machine_id`: ID único da máquina
- `name`: Nome da VM
- `django_url`: URL do Django

**Validações Automáticas:**
- `machine_id` deve ser único
- `port` deve estar entre 1 e 65535
- `fps` deve estar entre 1 e 120
- `trigger_interval_ms` deve ser >= 100

### 2. Gerenciar VM Específica

#### GET `/api/vms/{vm_id}`
Obtém detalhes completos de uma VM específica, incluindo ferramentas de inspeção.

#### PUT `/api/vms/{vm_id}`
Atualiza uma VM existente (suporte a atualização parcial).

**Campos Atualizáveis:**
- `name`, `description`, `django_url`, `ip_address`, `port`
- `source_type`, `camera_id`, `resolution_width`, `resolution_height`, `fps`
- `folder_path`, `rtsp_url`, `trigger_type`, `trigger_interval_ms`
- `inspection_config`, `mode`

#### DELETE `/api/vms/{vm_id}`
Remove uma VM (soft delete).

### 3. Ações da VM

#### POST `/api/vms/{vm_id}/action`
Executa ações na VM.

**Corpo da Requisição:**
```json
{
  "action": "start"
}
```

**Ações Disponíveis:**
- `start`: Inicia a VM
- `stop`: Para a VM
- `restart`: Reinicia a VM
- `trigger`: Executa trigger manual

**Validações:**
- Verifica se a ação pode ser executada no estado atual da VM
- Retorna erro 400 se a ação não for permitida

### 4. Ferramentas de Inspeção

#### GET `/api/vms/{vm_id}/tools`
Lista ferramentas de inspeção de uma VM.

#### POST `/api/vms/{vm_id}/tools`
Cria uma nova ferramenta de inspeção.

**Corpo da Requisição:**
```json
{
  "name": "Detector de Defeitos",
  "tool_type": "blob",
  "method": "threshold",
  "tool_config": {
    "threshold_value": 128,
    "min_area": 100
  },
  "roi_config": {
    "x": 100,
    "y": 100,
    "w": 200,
    "h": 200
  },
  "inspec_pass_fail": true,
  "normalize": false
}
```

**Tipos de Ferramenta:**
- `grayscale`: Filtro Grayscale
- `blob`: Detector de Blob
- `math`: Ferramenta Matemática
- `custom`: Personalizada

**Métodos:**
- `luminance`: Luminância
- `threshold`: Threshold
- `edge_detection`: Detecção de Bordas
- `pattern_matching`: Correspondência de Padrões

### 5. Heartbeats

#### GET `/api/vms/{vm_id}/heartbeats`
Lista heartbeats de uma VM.

**Parâmetros de Query:**
- `days` (int): Número de dias para buscar (padrão: 7, máximo: 365)
- `limit` (int): Limite de registros (padrão: 100, máximo: 1000)

### 6. Resumo de Status

#### GET `/api/vms/status/summary`
Retorna resumo do status de todas as VMs.

**Exemplo de Resposta:**
```json
{
  "total_vms": 5,
  "status_counts": {
    "running": 3,
    "stopped": 1,
    "error": 1
  },
  "connection_counts": {
    "connected": 4,
    "disconnected": 1
  },
  "mode_counts": {
    "PRODUCAO": 3,
    "TESTE": 2
  },
  "error_vms": [
    {
      "id": 3,
      "name": "Câmera com Problema",
      "error_message": "Falha na conexão com a câmera",
      "last_heartbeat": "2024-01-15T09:00:00Z"
    }
  ],
  "offline_vms": [],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Status das VMs

### Status de Operação
- `stopped`: Parada
- `running`: Executando
- `error`: Erro
- `maintenance`: Manutenção
- `offline`: Offline

### Status de Conexão
- `connected`: Conectado
- `disconnected`: Desconectado
- `connecting`: Conectando
- `error`: Erro de Conexão

### Modos de Operação
- `PRODUCAO`: Produção
- `TESTE`: Teste
- `DESENVOLVIMENTO`: Desenvolvimento

### Tipos de Fonte
- `camera`: Câmera Local
- `camera_IP`: Câmera IP
- `pasta`: Pasta de Imagens
- `rtsp`: Stream RTSP

### Tipos de Trigger
- `continuous`: Contínuo
- `manual`: Manual
- `external`: Externo
- `scheduled`: Agendado

## Autenticação e Segurança

- **Todas as rotas requerem autenticação** via `IsAuthenticated`
- **Validação automática** de dados via serializers DRF
- **Tratamento de erros padronizado** com códigos HTTP apropriados
- **Soft delete** para remoção segura de dados
- **Associação automática** de VMs ao usuário autenticado

## Tratamento de Erros

A API retorna erros padronizados com códigos HTTP apropriados:

```json
{
  "erro": "Descrição do erro",
  "details": {
    "campo": ["Lista de erros de validação"]
  }
}
```

**Códigos de Status:**
- `200 OK`: Sucesso
- `201 Created`: Recurso criado
- `400 Bad Request`: Dados inválidos
- `404 Not Found`: Recurso não encontrado
- `500 Internal Server Error`: Erro interno

## Exemplos de Uso

### Criar uma nova VM
```bash
curl -X POST http://localhost:8000/api/vms \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer seu_token" \
  -d '{
    "machine_id": "VM003",
    "name": "Câmera de Teste",
    "description": "VM para testes de desenvolvimento",
    "django_url": "http://localhost:5000",
    "source_type": "pasta",
    "folder_path": "./test_images"
  }'
```

### Iniciar uma VM
```bash
curl -X POST http://localhost:8000/api/vms/1/action \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer seu_token" \
  -d '{"action": "start"}'
```

### Obter resumo de status
```bash
curl -X GET http://localhost:8000/api/vms/status/summary \
  -H "Authorization: Bearer seu_token"
```

## Vantagens do DRF

✅ **Validação Automática**: Serializers validam dados automaticamente
✅ **Tratamento de Erros**: Respostas de erro padronizadas
✅ **Autenticação**: Sistema de permissões integrado
✅ **Documentação**: Auto-documentação via browsable API
✅ **Performance**: Otimizações automáticas de queries
✅ **Flexibilidade**: Suporte a atualizações parciais
✅ **Testes**: Framework de testes integrado

## Notas de Implementação

- Todas as VMs são associadas ao usuário que as criou
- Soft delete é usado para remoção (campo `is_active`)
- Heartbeats são mantidos por 7 dias por padrão
- Validações de campos são aplicadas automaticamente via serializers
- Paginação é implementada para listas grandes
- Filtros de busca são case-insensitive
- Suporte a atualizações parciais (PATCH) via PUT
- Tratamento de erros consistente em todas as views
