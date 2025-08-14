# Conexão Exclusiva Ponto-a-Ponto

## Visão Geral

O sistema de **conexão exclusiva** garante que cada máquina de visão Flask seja controlada por apenas um orquestrador Django por vez, implementando um mecanismo de **lock exclusivo** com heartbeat de ocupação.

## **🔒 Arquitetura de Conexão Exclusiva**

```
┌─────────────────────┐    ┌─────────────────────┐
│   Orquestrador A    │    │   Máquina Flask     │
│   (Conectado)       │◄──►│   (Lock Exclusivo)  │
│                     │    │                     │
└─────────────────────┘    └─────────────────────┘
         │                           │
         │                           │
         ▼                           ▼
┌─────────────────────┐    ┌─────────────────────┐
│   Orquestrador B    │    │   Heartbeat         │
│   (Tentativa)       │───►│   "OCUPADA"         │
│                     │    │                     │
└─────────────────────┘    └─────────────────────┘
```

## **🔄 Estados da Conexão**

### **1. Estado LIVRE**
- **Status**: `free`
- **Descrição**: Máquina disponível para conexão
- **Ação**: Aceita handshake de qualquer orquestrador
- **Transição**: Para `connected` após handshake bem-sucedido

### **2. Estado CONECTADO**
- **Status**: `connected`
- **Descrição**: Máquina conectada a um orquestrador
- **Ação**: Rejeita tentativas de outros orquestradores
- **Transição**: Para `free` após desconexão

### **3. Estado OCUPADA**
- **Status**: `occupied`
- **Descrição**: Máquina ocupada por outro orquestrador
- **Ação**: Responde "OCUPADA" para tentativas de conexão
- **Transição**: Para `free` após timeout ou desconexão

## **🤝 Handshake de Conexão Exclusiva**

### **Fase 1: Verificação de Disponibilidade**
```http
# Orquestrador verifica se máquina está livre
GET /api/machine/status/
```

**Resposta (LIVRE):**
```json
{
  "machine_id": "mv_abc123def456",
  "status": "free",
  "last_heartbeat": null,
  "connected_orchestrator": null,
  "ready_for_connection": true
}
```

**Resposta (OCUPADA):**
```json
{
  "machine_id": "mv_abc123def456",
  "status": "occupied",
  "last_heartbeat": "2025-08-13T20:10:00Z",
  "connected_orchestrator": "orch_xyz789",
  "ready_for_connection": false,
  "occupation_time": "2025-08-13T20:05:00Z"
}
```

### **Fase 2: Tentativa de Conexão**
```http
# Orquestrador tenta estabelecer conexão
POST /api/machine/connect/
{
  "orchestrator_id": "orch_abc123",
  "orchestrator_name": "Django-Main",
  "connection_type": "exclusive",
  "timeout_seconds": 300
}
```

**Resposta (Sucesso):**
```json
{
  "status": "connected",
  "connection_id": "conn_xyz789abc123",
  "session_token": "sess_abc123def456",
  "expires_at": "2025-08-13T21:10:00Z",
  "machine_config": {
    "supported_modes": ["run", "test"],
    "max_inspections": 5,
    "hardware_specs": {...}
  }
}
```

**Resposta (Falha - Ocupada):**
```json
{
  "status": "occupied",
  "error": "Machine is currently occupied by another orchestrator",
  "current_orchestrator": "orch_xyz789",
  "occupation_start": "2025-08-13T20:05:00Z",
  "estimated_release": "2025-08-13T20:15:00Z"
}
```

### **Fase 3: Estabelecimento da Sessão**
```http
# Orquestrador confirma conexão
POST /api/machine/session/establish/
{
  "connection_id": "conn_xyz789abc123",
  "session_token": "sess_abc123def456",
  "preferred_mode": "run",
  "config": {
    "webhook_interval": 2.0,
    "heartbeat_interval": 30
  }
}
```

## **💓 Heartbeat de Ocupação**

### **Estrutura do Heartbeat**
```json
{
  "machine_id": "mv_abc123def456",
  "orchestrator_id": "orch_abc123",
  "connection_id": "conn_xyz789abc123",
  "status": "connected",
  "heartbeat_type": "occupation",
  "timestamp": "2025-08-13T20:10:00Z",
  "occupation_duration": 300,  // segundos
  "active_inspections": 2,
  "machine_health": "good"
}
```

### **Resposta para Outros Orquestradores**
```http
# Outro orquestrador tenta conectar
GET /api/machine/status/
```

**Resposta com Heartbeat de Ocupação:**
```json
{
  "machine_id": "mv_abc123def456",
  "status": "occupied",
  "heartbeat": {
    "orchestrator_id": "orch_abc123",
    "connection_id": "conn_xyz789abc123",
    "last_heartbeat": "2025-08-13T20:10:00Z",
    "occupation_duration": 300,
    "active_inspections": 2
  },
  "message": "Machine is occupied by orchestrator orch_abc123",
  "estimated_release": "2025-08-13T20:15:00Z"
}
```

## **🔐 Implementação do Lock Exclusivo**

### **Classe de Controle de Conexão**
```python
import threading
import time
from datetime import datetime, timedelta

class ExclusiveConnectionManager:
    def __init__(self):
        self.connection_lock = threading.Lock()
        self.active_connection = None
        self.connection_timeout = 300  # 5 minutos
        
    def attempt_connection(self, orchestrator_id, orchestrator_name):
        """Tenta estabelecer conexão exclusiva"""
        with self.connection_lock:
            if self.active_connection is None:
                # Máquina livre - estabelece conexão
                self.active_connection = {
                    "orchestrator_id": orchestrator_id,
                    "orchestrator_name": orchestrator_name,
                    "connection_time": datetime.now(),
                    "last_heartbeat": datetime.now(),
                    "connection_id": self._generate_connection_id()
                }
                return {"status": "connected", "connection_id": self.active_connection["connection_id"]}
            else:
                # Máquina ocupada
                return {"status": "occupied", "current_orchestrator": self.active_connection["orchestrator_id"]}
    
    def release_connection(self, connection_id):
        """Libera conexão"""
        with self.connection_lock:
            if (self.active_connection and 
                self.active_connection["connection_id"] == connection_id):
                self.active_connection = None
                return True
            return False
    
    def update_heartbeat(self, connection_id):
        """Atualiza heartbeat da conexão ativa"""
        with self.connection_lock:
            if (self.active_connection and 
                self.active_connection["connection_id"] == connection_id):
                self.active_connection["last_heartbeat"] = datetime.now()
                return True
            return False
    
    def check_connection_timeout(self):
        """Verifica se conexão expirou por timeout"""
        with self.connection_lock:
            if self.active_connection:
                time_since_heartbeat = datetime.now() - self.active_connection["last_heartbeat"]
                if time_since_heartbeat.total_seconds() > self.connection_timeout:
                    self.active_connection = None
                    return True
            return False
    
    def get_connection_status(self):
        """Retorna status atual da conexão"""
        with self.connection_lock:
            if self.active_connection:
                return {
                    "status": "occupied",
                    "orchestrator_id": self.active_connection["orchestrator_id"],
                    "connection_time": self.active_connection["connection_time"],
                    "last_heartbeat": self.active_connection["last_heartbeat"],
                    "occupation_duration": (datetime.now() - self.active_connection["connection_time"]).total_seconds()
                }
            else:
                return {"status": "free"}
    
    def _generate_connection_id(self):
        """Gera ID único para conexão"""
        return f"conn_{int(time.time())}_{hash(str(self.active_connection))}"
```

### **Middleware de Autenticação**
```python
from functools import wraps
from flask import request, jsonify

def require_exclusive_connection(f):
    """Decorator para endpoints que requerem conexão exclusiva"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        connection_id = request.headers.get('X-Connection-ID')
        if not connection_id:
            return jsonify({"error": "Connection ID required"}), 401
        
        if not connection_manager.is_valid_connection(connection_id):
            return jsonify({"error": "Invalid or expired connection"}), 401
        
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/machine/inspection/start', methods=['POST'])
@require_exclusive_connection
def start_inspection():
    """Inicia inspeção (requer conexão exclusiva)"""
    # Lógica da inspeção
    pass
```

## **📡 Endpoints de Controle de Conexão**

### **1. Verificar Status**
```http
GET /api/machine/connection/status/
```

**Resposta:**
```json
{
  "machine_id": "mv_abc123def456",
  "connection_status": "occupied",
  "current_connection": {
    "orchestrator_id": "orch_abc123",
    "orchestrator_name": "Django-Main",
    "connection_id": "conn_xyz789abc123",
    "connection_time": "2025-08-13T20:05:00Z",
    "last_heartbeat": "2025-08-13T20:10:00Z",
    "occupation_duration": 300
  },
  "ready_for_new_connection": false
}
```

### **2. Forçar Desconexão (Admin)**
```http
POST /api/machine/connection/force_disconnect/
{
  "reason": "Maintenance required",
  "admin_token": "admin_xyz789"
}
```

### **3. Listar Orquestradores na Fila**
```http
GET /api/machine/connection/queue/
```

**Resposta:**
```json
{
  "queue": [
    {
      "orchestrator_id": "orch_def456",
      "orchestrator_name": "Django-Backup",
      "request_time": "2025-08-13T20:08:00Z",
      "priority": "normal"
    }
  ],
  "estimated_wait_time": 120
}
```

## **🚨 Tratamento de Conflitos**

### **1. Tentativa de Conexão Simultânea**
```python
def handle_simultaneous_connection_attempts(self, orchestrator_a, orchestrator_b):
    """Trata tentativas simultâneas de conexão"""
    # Prioriza por timestamp
    if orchestrator_a["timestamp"] < orchestrator_b["timestamp"]:
        winner = orchestrator_a
        loser = orchestrator_b
    else:
        winner = orchestrator_b
        loser = orchestrator_a
    
    # Estabelece conexão para o vencedor
    connection_result = self.attempt_connection(winner["id"], winner["name"])
    
    # Notifica o perdedor
    self._notify_connection_rejected(loser["id"], "Machine occupied by earlier request")
    
    return connection_result
```

### **2. Timeout de Conexão**
```python
def handle_connection_timeout(self):
    """Trata timeout de conexão"""
    if self.check_connection_timeout():
        # Notifica orquestrador sobre desconexão
        if self.active_connection:
            self._notify_connection_timeout(self.active_connection["orchestrator_id"])
        
        # Libera conexão
        self.release_connection(self.active_connection["connection_id"])
        
        # Log do evento
        logger.warning(f"Connection timeout - machine {self.machine_id} is now free")
```

### **3. Reconexão Automática**
```python
def handle_reconnection_attempt(self, orchestrator_id, connection_id):
    """Trata tentativa de reconexão"""
    if (self.active_connection and 
        self.active_connection["orchestrator_id"] == orchestrator_id):
        
        # Atualiza heartbeat
        self.update_heartbeat(connection_id)
        
        return {
            "status": "reconnected",
            "connection_id": connection_id,
            "message": "Reconnection successful"
        }
    else:
        return {
            "status": "failed",
            "error": "Invalid reconnection attempt"
        }
```

## **📊 Monitoramento de Conexões**

### **Métricas de Conexão**
```json
{
  "connection_metrics": {
    "total_connections": 45,
    "average_connection_duration": 1800,  // segundos
    "connection_success_rate": 98.5,
    "timeout_events": 2,
    "forced_disconnections": 1,
    "queue_wait_time_average": 45
  },
  "current_status": {
    "machine_id": "mv_abc123def456",
    "connection_status": "occupied",
    "uptime": 86400,  // segundos
    "last_status_change": "2025-08-13T20:05:00Z"
  }
}
```

## **🔧 Configuração**

### **Parâmetros de Conexão**
```json
{
  "connection": {
    "timeout_seconds": 300,
    "heartbeat_interval": 30,
    "max_connection_attempts": 3,
    "queue_enabled": true,
    "max_queue_size": 10,
    "auto_reconnect": true,
    "force_disconnect_admin_only": true
  }
}
```

## **Próximos Passos**

1. [Autenticação Mútua](./README.md) - Sistema de segurança completo
2. [Modos de Operação](./../02-APIs/Modos-Operacao.md) - Controle de modos
3. [Tratamento de Conflitos](./../05-Tratamento-Erros/Conflitos-Conexao.md) - Resolução de conflitos
4. [Implementação](./Implementacao.md) - Código completo de exemplo
