# API Django (Orquestrador)

## Visão Geral

A API Django atua como **orquestrador central** do sistema AnalyticLens, gerenciando máquinas de visão, distribuindo inspeções e coletando resultados via webhooks.

## Base URL

```
https://django-server.com/api/v1/
```

## Autenticação

Todas as requisições devem incluir o header de autenticação:

```http
Authorization: Bearer <session_token>
```

## Endpoints

### 1. **Gestão de Máquinas de Visão**

#### **Listar Máquinas**
```http
GET /machines/
```

**Resposta:**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "mv_abc123def456",
      "name": "MV-Factory-A",
      "location": "Linha de Produção A",
      "ip_address": "192.168.1.100",
      "port": 5000,
      "status": "online",
      "last_heartbeat": "2025-08-13T20:10:00Z",
      "max_concurrent_inspections": 2,
      "current_inspections": 1,
      "supported_inspection_types": ["blob_detection", "edge_detection"],
      "hardware_specs": {
        "gpu": "RTX 3080",
        "cpu": "Intel i7-10700K",
        "memory": "32GB"
      },
      "is_available": true
    }
  ]
}
```

#### **Obter Máquina Específica**
```http
GET /machines/{machine_id}/
```

#### **Cadastrar Nova Máquina**
```http
POST /machines/
```

**Payload:**
```json
{
  "name": "MV-Factory-B",
  "location": "Linha de Produção B",
  "ip_address": "192.168.1.101",
  "port": 5000,
  "max_concurrent_inspections": 3,
  "supported_inspection_types": ["blob_detection", "color_filter"],
  "hardware_specs": {
    "gpu": "RTX 3070",
    "cpu": "Intel i5-10600K",
    "memory": "16GB"
  }
}
```

#### **Atualizar Máquina**
```http
PUT /machines/{machine_id}/
PATCH /machines/{machine_id}/
```

#### **Remover Máquina**
```http
DELETE /machines/{machine_id}/
```

#### **Status da Máquina**
```http
GET /machines/{machine_id}/status/
```

**Resposta:**
```json
{
  "machine_id": "mv_abc123def456",
  "status": "online",
  "last_heartbeat": "2025-08-13T20:10:00Z",
  "current_inspections": 1,
  "system_info": {
    "cpu_usage": 45.2,
    "memory_usage": 67.8,
    "gpu_usage": 23.1,
    "temperature": 42.5
  },
  "performance_metrics": {
    "inspections_per_hour": 12,
    "average_processing_time": 2.3,
    "success_rate": 98.5
  }
}
```

### 2. **Gestão de Inspeções**

#### **Listar Inspeções**
```http
GET /inspections/
```

**Parâmetros de Query:**
- `status`: Filtro por status (pending, assigned, processing, completed, failed)
- `machine_id`: Filtro por máquina específica
- `inspection_type`: Filtro por tipo de inspeção
- `created_after`: Filtro por data de criação
- `page`: Paginação

#### **Criar Nova Inspeção**
```http
POST /inspections/
```

**Payload:**
```json
{
  "name": "Inspeção de Qualidade A",
  "description": "Verificação de defeitos na linha A",
  "inspection_type": "blob_detection",
  "pipeline_config": {
    "tools": [
      {
        "name": "image_source",
        "parameters": {
          "source_type": "file",
          "file_path": "/path/to/image.jpg"
        }
      },
      {
        "name": "blob_detection",
        "parameters": {
          "min_area": 100,
          "max_area": 10000,
          "threshold": 128
        }
      }
    ],
    "connections": [
      {
        "from": "image_source",
        "to": "blob_detection"
      }
    ]
  },
  "priority": 2,
  "target_machine_id": "mv_abc123def456"
}
```

#### **Obter Inspeção Específica**
```http
GET /inspections/{inspection_id}/
```

#### **Atualizar Inspeção**
```http
PUT /inspections/{inspection_id}/
PATCH /inspections/{inspection_id}/
```

#### **Enviar para Máquina**
```http
POST /inspections/{inspection_id}/send/
```

**Payload:**
```json
{
  "target_machine_id": "mv_abc123def456",
  "priority": 1
}
```

#### **Cancelar Inspeção**
```http
POST /inspections/{inspection_id}/cancel/
```

### 3. **Orquestração**

#### **Distribuir Inspeção Automaticamente**
```http
POST /orchestrator/distribute/
```

**Payload:**
```json
{
  "inspection_id": "ins_xyz789abc123",
  "strategy": "load_balanced",  // ou "nearest", "specialized"
  "preferred_machines": ["mv_abc123def456"]
}
```

#### **Gerenciar Fila**
```http
GET /orchestrator/queue/
```

**Resposta:**
```json
{
  "pending_inspections": [
    {
      "id": "ins_xyz789abc123",
      "priority": 1,
      "queued_at": "2025-08-13T20:05:00Z",
      "estimated_wait_time": 300
    }
  ],
  "machine_assignments": {
    "mv_abc123def456": {
      "current_inspections": 1,
      "queue_position": 0
    }
  }
}
```

### 4. **Webhooks (Recebimento)**

#### **Receber Resultados**
```http
POST /webhooks/results/
```

**Payload (enviado pela máquina Flask):**
```json
{
  "machine_id": "mv_abc123def456",
  "inspection_id": "ins_xyz789abc123",
  "status": "completed",
  "results": {
    "blob_count": 5,
    "blob_locations": [
      {"x": 100, "y": 150, "width": 50, "height": 30},
      {"x": 200, "y": 300, "width": 40, "height": 25}
    ],
    "processing_time": 2.3,
    "confidence_score": 0.95
  },
  "error_message": null,
  "timestamp": "2025-08-13T20:10:00Z"
}
```

#### **Receber Heartbeat**
```http
POST /webhooks/heartbeat/
```

**Payload:**
```json
{
  "machine_id": "mv_abc123def456",
  "status": "online",
  "system_info": {
    "cpu_usage": 45.2,
    "memory_usage": 67.8,
    "gpu_usage": 23.1,
    "temperature": 42.5
  },
  "performance_metrics": {
    "inspections_per_hour": 12,
    "average_processing_time": 2.3,
    "success_rate": 98.5
  },
  "timestamp": "2025-08-13T20:10:00Z"
}
```

#### **Receber Status Update**
```http
POST /webhooks/status/
```

**Payload:**
```json
{
  "machine_id": "mv_abc123def456",
  "status": "busy",
  "current_inspections": 2,
  "timestamp": "2025-08-13T20:10:00Z"
}
```

### 5. **Monitoramento e Estatísticas**

#### **Dashboard Geral**
```http
GET /dashboard/
```

**Resposta:**
```json
{
  "total_machines": 5,
  "online_machines": 4,
  "total_inspections": 150,
  "pending_inspections": 12,
  "processing_inspections": 8,
  "completed_inspections": 125,
  "failed_inspections": 5,
  "system_health": "good",
  "performance_metrics": {
    "average_processing_time": 2.1,
    "throughput_per_hour": 45,
    "success_rate": 96.7
  }
}
```

#### **Estatísticas por Máquina**
```http
GET /machines/{machine_id}/statistics/
```

**Parâmetros de Query:**
- `period`: Período (hour, day, week, month)
- `start_date`: Data de início
- `end_date`: Data de fim

## Códigos de Status HTTP

- **200**: Sucesso
- **201**: Criado com sucesso
- **400**: Erro de validação
- **401**: Não autorizado
- **403**: Proibido
- **404**: Não encontrado
- **409**: Conflito
- **422**: Entidade não processável
- **500**: Erro interno do servidor

## Paginação

Para endpoints que retornam listas, a paginação segue o padrão:

```json
{
  "count": 100,
  "next": "https://api.example.com/endpoint/?page=3",
  "previous": "https://api.example.com/endpoint/?page=1",
  "results": [...]
}
```

## Rate Limiting

- **Máquinas de Visão**: 100 requisições por minuto
- **Usuários**: 1000 requisições por hora
- **Webhooks**: Sem limite (crítico para operação)

## Versionamento

A API usa versionamento por URL (`/api/v1/`). Mudanças incompatíveis resultarão em nova versão.

## Próximos Passos

1. [API Flask](./API-Flask.md) - Especificação das máquinas de visão
2. [Endpoints Comuns](./Endpoints.md) - Padrões compartilhados
3. [Implementação](./Implementacao.md) - Código de exemplo
4. [Testes](./Testes.md) - Casos de teste da API
