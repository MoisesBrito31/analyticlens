# Modos de Operação das Máquinas de Visão

## Visão Geral

As máquinas de visão Flask operam em dois modos distintos, cada um otimizado para diferentes cenários de uso e requisitos de performance.

## **🔄 Modo RUN (Execução Contínua)**

### **Características**
- **Comportamento**: Execução contínua e automática de inspeções
- **Performance**: Máxima velocidade de processamento
- **Timing**: Webhook a cada 2 segundos (configurável)
- **Uso**: Produção, monitoramento contínuo, linha de produção

### **Funcionamento**
```
1. VM recebe configuração de inspeção
2. Inicia processamento contínuo
3. A cada 2s: envia webhook com resultados + imagem
4. Continua processando próxima inspeção
5. Mantém logs em memória para streaming
```

### **Configuração**
```json
{
  "mode": "run",
  "webhook_interval": 2.0,  // segundos
  "continuous_processing": true,
  "auto_restart": true,
  "max_queue_size": 100
}
```

### **Endpoints Específicos**
```http
# Ativar modo RUN
POST /api/machine/mode/run/
{
  "webhook_interval": 2.0,
  "continuous_processing": true
}

# Configurar parâmetros do modo RUN
PUT /api/machine/mode/run/config/
{
  "webhook_interval": 1.5,
  "max_queue_size": 200,
  "auto_restart": true
}
```

## **🧪 Modo TESTE (Processamento Controlado)**

### **Características**
- **Comportamento**: Processamento controlado com delay
- **Performance**: Controlada para análise detalhada
- **Timing**: Resposta máxima a cada 2 segundos
- **Uso**: Desenvolvimento, teste, validação, debug

### **Funcionamento**
```
1. VM recebe configuração de inspeção
2. Processa com delay controlado
3. Aguarda até 2s antes de responder
4. Envia resultado completo
5. Aguarda próxima instrução
```

### **Configuração**
```json
{
  "mode": "test",
  "max_response_time": 2.0,  // segundos
  "detailed_logging": true,
  "step_by_step": false,
  "debug_mode": true
}
```

### **Endpoints Específicos**
```http
# Ativar modo TESTE
POST /api/machine/mode/test/
{
  "max_response_time": 2.0,
  "detailed_logging": true
}

# Executar inspeção passo a passo
POST /api/machine/test/step/
{
  "inspection_id": "ins_xyz789",
  "step_number": 1
}

# Configurar parâmetros do modo TESTE
PUT /api/machine/mode/test/config/
{
  "max_response_time": 1.5,
  "detailed_logging": true,
  "step_by_step": true
}
```

## **📊 Comparação dos Modos**

| Aspecto | Modo RUN | Modo TESTE |
|---------|----------|-------------|
| **Performance** | Máxima | Controlada |
| **Timing** | A cada 2s | Máximo 2s |
| **Uso de CPU** | 100% | Configurável |
| **Logs** | Básicos | Detalhados |
| **Debug** | Limitado | Completo |
| **Produção** | ✅ Ideal | ❌ Não recomendado |
| **Desenvolvimento** | ❌ Limitado | ✅ Ideal |

## **🔧 Controle de Modos**

### **Mudança de Modo**
```http
# Mudar para modo RUN
POST /api/machine/mode/change/
{
  "new_mode": "run",
  "config": {
    "webhook_interval": 2.0,
    "continuous_processing": true
  }
}

# Mudar para modo TESTE
POST /api/machine/mode/change/
{
  "new_mode": "test",
  "config": {
    "max_response_time": 2.0,
    "detailed_logging": true
  }
}
```

### **Status do Modo Atual**
```http
GET /api/machine/mode/status/
```

**Resposta:**
```json
{
  "current_mode": "run",
  "mode_config": {
    "webhook_interval": 2.0,
    "continuous_processing": true,
    "auto_restart": true
  },
  "mode_started_at": "2025-08-13T20:10:00Z",
  "inspections_processed": 45,
  "current_queue_size": 12
}
```

## **📡 Webhooks por Modo**

### **Modo RUN - Webhook Contínuo**
```json
{
  "machine_id": "mv_abc123def456",
  "mode": "run",
  "webhook_type": "continuous_results",
  "data": {
    "inspection_id": "ins_xyz789abc123",
    "status": "processing",
    "results": {
      "blob_count": 3,
      "processing_time": 1.8,
      "confidence_score": 0.92
    },
    "image_stream": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...",
    "timestamp": "2025-08-13T20:10:00Z"
  }
}
```

### **Modo TESTE - Resposta Controlada**
```json
{
  "machine_id": "mv_abc123def456",
  "mode": "test",
  "webhook_type": "test_results",
  "data": {
    "inspection_id": "ins_xyz789abc123",
    "status": "completed",
    "results": {
      "blob_count": 3,
      "blob_details": [
        {
          "x": 100, "y": 150,
          "width": 50, "height": 30,
          "confidence": 0.95,
          "area": 1500
        }
      ],
      "processing_time": 1.8,
      "confidence_score": 0.92,
      "debug_info": {
        "steps_executed": 5,
        "intermediate_results": [...],
        "performance_metrics": {...}
      }
    },
    "image_stream": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...",
    "timestamp": "2025-08-13T20:10:00Z"
  }
}
```

## **💾 Sistema de Logs em Memória**

### **Estrutura de Logs**
```python
class MemoryLogger:
    def __init__(self, max_logs=1000, retention_hours=24):
        self.max_logs = max_logs
        self.retention_hours = retention_hours
        self.logs = []
        self.image_cache = {}
    
    def add_log(self, inspection_id, results, image_data):
        """Adiciona log à memória"""
        log_entry = {
            "inspection_id": inspection_id,
            "timestamp": time.time(),
            "results": results,
            "image_checksum": hashlib.md5(image_data).hexdigest()
        }
        
        self.logs.append(log_entry)
        self.image_cache[log_entry["image_checksum"]] = image_data
        
        # Limpa logs antigos
        self._cleanup_old_logs()
    
    def get_logs(self, hours_back=1):
        """Retorna logs das últimas N horas"""
        cutoff_time = time.time() - (hours_back * 3600)
        return [log for log in self.logs if log["timestamp"] > cutoff_time]
```

### **Streaming de Logs**
```http
# Stream de logs em tempo real
GET /api/machine/logs/stream/
```

**Headers de resposta:**
```http
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
```

**Formato SSE (Server-Sent Events):**
```
event: log_update
data: {"inspection_id": "ins_xyz789", "timestamp": "2025-08-13T20:10:00Z"}

event: image_available
data: {"checksum": "abc123", "size": 2048576}
```

## **⚙️ Configuração Avançada**

### **Parâmetros de Performance**
```json
{
  "run_mode": {
    "webhook_interval": 2.0,
    "max_queue_size": 100,
    "auto_restart": true,
    "cpu_threshold": 80,
    "memory_threshold": 85
  },
  "test_mode": {
    "max_response_time": 2.0,
    "detailed_logging": true,
    "step_by_step": false,
    "debug_mode": true,
    "save_intermediate": true
  },
  "logging": {
    "max_logs": 1000,
    "retention_hours": 24,
    "image_compression": "JPEG",
    "image_quality": 85,
    "stream_buffer_size": 1024
  }
}
```

### **Transição Suave entre Modos**
```python
class ModeController:
    def change_mode(self, new_mode, config):
        """Muda modo com transição suave"""
        # Para processamento atual
        self._stop_current_processing()
        
        # Salva estado atual
        current_state = self._save_current_state()
        
        # Configura novo modo
        self._configure_mode(new_mode, config)
        
        # Restaura estado se necessário
        if config.get("restore_state", False):
            self._restore_state(current_state)
        
        # Inicia novo modo
        self._start_mode(new_mode)
```

## **🔍 Monitoramento e Métricas**

### **Métricas por Modo**
```json
{
  "run_mode_metrics": {
    "inspections_per_minute": 30,
    "average_processing_time": 1.8,
    "webhook_success_rate": 99.5,
    "queue_utilization": 75.2
  },
  "test_mode_metrics": {
    "inspections_completed": 15,
    "average_response_time": 1.2,
    "debug_sessions": 8,
    "step_executions": 45
  }
}
```

## **🚨 Tratamento de Erros**

### **Erros Específicos por Modo**
```python
class ModeErrorHandler:
    def handle_run_mode_error(self, error):
        """Trata erros no modo RUN"""
        if error.type == "queue_overflow":
            # Reduz frequência de webhook
            self._reduce_webhook_frequency()
        elif error.type == "processing_timeout":
            # Reinicia pipeline
            self._restart_processing_pipeline()
    
    def handle_test_mode_error(self, error):
        """Trata erros no modo TESTE"""
        if error.type == "response_timeout":
            # Aumenta timeout
            self._increase_response_timeout()
        elif error.type == "debug_failure":
            # Ativa modo de emergência
            self._activate_emergency_mode()
```

## **Próximos Passos**

1. [API Flask](./API-Flask.md) - Implementação completa das APIs
2. [Controle de Modos](./../06-Fluxos/Controle-Modos.md) - Fluxos de controle
3. [Streaming de Logs](./../06-Fluxos/Streaming-Logs.md) - Implementação do streaming
4. [Configuração](./../07-Exemplos/Configuracao-Modos.md) - Exemplos de configuração
