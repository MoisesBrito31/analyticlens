# Webhooks e Comunicação Assíncrona

## Visão Geral

Os webhooks são o mecanismo principal de comunicação assíncrona entre as **Máquinas de Visão Flask** e o **Django Orquestrador**. Eles permitem que as máquinas notifiquem o Django sobre eventos importantes sem necessidade de polling.

## Arquitetura de Webhooks

```
┌─────────────────────┐    ┌─────────────────────┐
│   Máquina Flask     │    │   Django Server     │
│   (Visão Comput.)   │    │   (Orquestrador)    │
│                     │    │                     │
│   • Processa        │    │   • Recebe          │
│     inspeção        │    │     webhooks        │
│   • Gera resultados │    │   • Atualiza        │
│   • Envia webhook   │───►│     status          │
│                     │    │   • Notifica        │
│                     │    │     frontend        │
└─────────────────────┘    └─────────────────────┘
```

## Tipos de Webhook

### 1. **Resultados de Inspeção**
- **Endpoint**: `/api/webhooks/results/`
- **Método**: POST
- **Frequência**: Após cada inspeção concluída
- **Payload**: Resultados completos da inspeção

### 2. **Heartbeat (Pulso)**
- **Endpoint**: `/api/webhooks/heartbeat/`
- **Método**: POST
- **Frequência**: A cada 30 segundos
- **Payload**: Status da máquina e métricas

### 3. **Atualizações de Status**
- **Endpoint**: `/api/webhooks/status/`
- **Método**: POST
- **Frequência**: Quando status muda
- **Payload**: Novo status e informações

### 4. **Logs de Sistema**
- **Endpoint**: `/api/webhooks/logs/`
- **Método**: POST
- **Frequência**: Quando necessário
- **Payload**: Logs de erro ou eventos importantes

## Estrutura dos Webhooks

### **Headers Padrão**
```http
Content-Type: application/json
User-Agent: AnalyticLens-Machine/1.0.0
X-Machine-ID: mv_abc123def456
X-Webhook-Type: results|heartbeat|status|logs
X-Timestamp: 2025-08-13T20:10:00Z
X-Signature: sha256=abc123...
```

### **Payload Base**
```json
{
  "machine_id": "mv_abc123def456",
  "timestamp": "2025-08-13T20:10:00Z",
  "version": "1.0.0",
  "data": {
    // Dados específicos do tipo de webhook
  }
}
```

## Implementação

### **Máquina Flask (Envio)**
```python
import requests
import json
import hashlib
import time

class WebhookSender:
    def __init__(self, django_url, machine_id, secret_key):
        self.django_url = django_url
        self.machine_id = machine_id
        self.secret_key = secret_key
    
    def send_webhook(self, webhook_type, data):
        """Envia webhook para o Django"""
        payload = {
            "machine_id": self.machine_id,
            "timestamp": time.time(),
            "version": "1.0.0",
            "data": data
        }
        
        # Gera assinatura para segurança
        signature = self._generate_signature(payload)
        
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "AnalyticLens-Machine/1.0.0",
            "X-Machine-ID": self.machine_id,
            "X-Webhook-Type": webhook_type,
            "X-Timestamp": str(payload["timestamp"]),
            "X-Signature": signature
        }
        
        try:
            response = requests.post(
                f"{self.django_url}/api/webhooks/{webhook_type}/",
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, f"Erro {response.status_code}: {response.text}"
                
        except Exception as e:
            return False, f"Erro de conexão: {str(e)}"
    
    def _generate_signature(self, payload):
        """Gera assinatura HMAC do payload"""
        message = json.dumps(payload, sort_keys=True)
        signature = hashlib.sha256(
            (message + self.secret_key).encode()
        ).hexdigest()
        return f"sha256={signature}"
```

### **Django (Recebimento)**
```python
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import hashlib
import hmac

@csrf_exempt
@require_http_methods(["POST"])
def webhook_results(request):
    """Recebe webhook de resultados de inspeção"""
    try:
        # Valida headers
        machine_id = request.headers.get('X-Machine-ID')
        webhook_type = request.headers.get('X-Webhook-Type')
        timestamp = request.headers.get('X-Timestamp')
        signature = request.headers.get('X-Signature')
        
        if not all([machine_id, webhook_type, timestamp, signature]):
            return JsonResponse(
                {"error": "Headers obrigatórios ausentes"}, 
                status=400
            )
        
        # Valida assinatura
        if not _validate_signature(request.body, signature, machine_id):
            return JsonResponse(
                {"error": "Assinatura inválida"}, 
                status=401
            )
        
        # Processa payload
        payload = json.loads(request.body)
        
        # Atualiza banco de dados
        _process_results_webhook(payload)
        
        # Notifica frontend via WebSocket
        _notify_frontend(payload)
        
        return JsonResponse({"status": "success"})
        
    except Exception as e:
        return JsonResponse(
            {"error": f"Erro interno: {str(e)}"}, 
            status=500
        )

def _validate_signature(body, signature, machine_id):
    """Valida assinatura HMAC do webhook"""
    # Busca chave secreta da máquina
    machine = InspectionMachine.objects.get(id=machine_id)
    secret_key = machine.secret_key
    
    # Gera assinatura esperada
    expected_signature = hmac.new(
        secret_key.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    return signature == f"sha256={expected_signature}"
```

## Tratamento de Falhas

### **Estratégias de Retry**
```python
class WebhookRetry:
    def __init__(self, max_retries=3, backoff_factor=2):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
    
    def send_with_retry(self, webhook_sender, webhook_type, data):
        """Envia webhook com retry automático"""
        for attempt in range(self.max_retries):
            try:
                success, response = webhook_sender.send_webhook(
                    webhook_type, data
                )
                
                if success:
                    return True, response
                
                # Aguarda antes do próximo tentativa
                if attempt < self.max_retries - 1:
                    wait_time = self.backoff_factor ** attempt
                    time.sleep(wait_time)
                    
            except Exception as e:
                if attempt == self.max_retries - 1:
                    return False, f"Falha após {self.max_retries} tentativas: {str(e)}"
        
        return False, "Número máximo de tentativas excedido"
```

### **Fila de Webhooks Falhados**
```python
class WebhookQueue:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.queue_key = "webhook_queue"
    
    def enqueue_failed_webhook(self, webhook_data):
        """Adiciona webhook falhado à fila para retry posterior"""
        self.redis.lpush(self.queue_key, json.dumps(webhook_data))
    
    def process_failed_webhooks(self):
        """Processa webhooks falhados da fila"""
        while True:
            webhook_data = self.redis.brpop(self.queue_key, timeout=1)
            if webhook_data:
                self._retry_webhook(json.loads(webhook_data[1]))
```

## Monitoramento e Logs

### **Métricas de Webhook**
- **Taxa de sucesso**: % de webhooks entregues com sucesso
- **Latência**: Tempo médio de entrega
- **Falhas**: Número e tipos de falhas
- **Retry**: Número médio de tentativas por webhook

### **Logs de Auditoria**
```python
import logging

logger = logging.getLogger('webhooks')

def log_webhook_event(machine_id, webhook_type, status, details):
    """Registra evento de webhook para auditoria"""
    logger.info(
        f"Webhook {webhook_type} da máquina {machine_id}: {status}",
        extra={
            'machine_id': machine_id,
            'webhook_type': webhook_type,
            'status': status,
            'details': details,
            'timestamp': time.time()
        }
    )
```

## Configuração

### **Parâmetros Recomendados**
- **Timeout**: 10 segundos para requisições
- **Retry**: Máximo 3 tentativas com backoff exponencial
- **Heartbeat**: A cada 30 segundos
- **Fila de Retry**: Processar a cada 5 minutos
- **Logs**: Manter por 90 dias

### **Variáveis de Ambiente**
```bash
# Máquina Flask
DJANGO_WEBHOOK_URL=https://django-server.com/api/webhooks
WEBHOOK_SECRET_KEY=your_secret_key_here
HEARTBEAT_INTERVAL=30
MAX_RETRY_ATTEMPTS=3

# Django
WEBHOOK_SECRET_KEYS={"mv_abc123": "key1", "mv_def456": "key2"}
WEBHOOK_TIMEOUT=10
WEBHOOK_MAX_RETRIES=3
```

## Próximos Passos

1. [Heartbeat](./Heartbeat.md) - Detalhes do sistema de pulso
2. [Resultados](./Resultados.md) - Estrutura dos resultados de inspeção
3. [Implementação](./Implementacao.md) - Código completo de exemplo
4. [Testes](./Testes.md) - Casos de teste dos webhooks
