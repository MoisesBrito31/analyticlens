# Configuração Local da Máquina de Visão

## Visão Geral

As **máquinas de visão Flask** gerenciam **localmente** suas configurações de **source de imagens** e **tipo de trigger**, eliminando a necessidade de ferramentas externas de configuração. O orquestrador Django apenas envia **configurações de inspeção** (algoritmos, parâmetros, regras).

## **🔄 Arquitetura de Configuração Local**

```
┌─────────────────────┐    ┌─────────────────────┐
│   Django            │    │   VM Flask          │
│   Orquestrador      │◄──►│   (Configurada)     │
│                     │    │                     │
│   • Envia           │    │   • Source Config   │
│     inspeções       │    │   • Trigger Config  │
│   • Recebe          │    │   • Capture Params  │
│     resultados      │    │   • Local Control   │
│   • Controla modo   │    │   • Auto-start      │
└─────────────────────┘    └─────────────────────┘
```

## **📷 Configuração de Source de Imagens**

### **1. Tipos de Source Suportados**

#### **Câmera USB**
```json
{
  "source_type": "usb_camera",
  "config": {
    "device_id": 0,
    "resolution": {
      "width": 1920,
      "height": 1080
    },
    "fps": 30,
    "format": "MJPG",
    "auto_exposure": true,
    "gain": 1.0,
    "brightness": 50,
    "contrast": 50
  }
}
```

#### **Stream RTSP/HTTP**
```json
{
  "source_type": "rtsp_stream",
  "config": {
    "url": "rtsp://192.168.1.100:554/stream1",
    "username": "admin",
    "password": "password123",
    "timeout": 5000,
    "buffer_size": 1024,
    "reconnect_interval": 30
  }
}
```

#### **Arquivo de Vídeo**
```json
{
  "source_type": "video_file",
  "config": {
    "file_path": "/data/videos/inspection.mp4",
    "loop": true,
    "start_frame": 0,
    "end_frame": -1,
    "playback_speed": 1.0
  }
}
```

#### **Diretório de Imagens**
```json
{
  "source_type": "image_directory",
  "config": {
    "directory_path": "/data/images/",
    "file_pattern": "*.jpg",
    "sort_by": "timestamp",
    "recursive": false,
    "refresh_interval": 5
  }
}
```

### **2. Configuração via Arquivo Local**
```python
# config/source_config.py
class SourceConfiguration:
    def __init__(self):
        self.config_file = "config/source.json"
        self.load_config()
    
    def load_config(self):
        """Carrega configuração do arquivo local"""
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = self._default_config()
            self.save_config()
    
    def _default_config(self):
        """Configuração padrão"""
        return {
            "source_type": "usb_camera",
            "config": {
                "device_id": 0,
                "resolution": {"width": 640, "height": 480},
                "fps": 30,
                "format": "MJPG"
            }
        }
    
    def save_config(self):
        """Salva configuração no arquivo local"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
```

## **⚡ Configuração de Trigger**

### **1. Tipos de Trigger**

#### **Trigger Contínuo**
```json
{
  "trigger_type": "continuous",
  "config": {
    "interval_ms": 2000,
    "max_fps": 30,
    "adaptive_timing": true,
    "skip_frames": false
  }
}
```

#### **Trigger por Evento (Motion Detection)**
```json
{
  "trigger_type": "motion_event",
  "config": {
    "sensitivity": 0.1,
    "min_area": 100,
    "debounce_ms": 500,
    "motion_threshold": 25,
    "background_subtraction": true
  }
}
```

#### **Trigger Manual**
```json
{
  "trigger_type": "manual",
  "config": {
    "enable_http_endpoint": true,
    "enable_websocket": true,
    "require_authentication": true,
    "max_queue_size": 10
  }
}
```

#### **Trigger Agendado**
```json
{
  "trigger_type": "scheduled",
  "config": {
    "cron_expression": "*/5 * * * *",  // A cada 5 minutos
    "timezone": "America/Sao_Paulo",
    "enable_dst": true,
    "fallback_to_continuous": false
  }
}
```

### **2. Implementação do Trigger Controller**
```python
class TriggerController:
    def __init__(self, config):
        self.config = config
        self.trigger_type = config["trigger_type"]
        self.trigger_config = config["config"]
        self.is_active = False
        self.last_trigger = None
        
    def start(self):
        """Inicia o sistema de trigger"""
        self.is_active = True
        
        if self.trigger_type == "continuous":
            self._start_continuous_trigger()
        elif self.trigger_type == "motion_event":
            self._start_motion_detection()
        elif self.trigger_type == "scheduled":
            self._start_scheduled_trigger()
        elif self.trigger_type == "manual":
            self._start_manual_trigger()
    
    def _start_continuous_trigger(self):
        """Inicia trigger contínuo"""
        interval = self.trigger_config["interval_ms"] / 1000.0
        
        def continuous_loop():
            while self.is_active:
                self._trigger_capture()
                time.sleep(interval)
        
        threading.Thread(target=continuous_loop, daemon=True).start()
    
    def _start_motion_detection(self):
        """Inicia detecção de movimento"""
        def motion_detection_loop():
            while self.is_active:
                if self._detect_motion():
                    self._trigger_capture()
                time.sleep(0.1)  # 100ms polling
        
        threading.Thread(target=motion_detection_loop, daemon=True).start()
    
    def _detect_motion(self):
        """Detecta movimento na imagem"""
        # Implementação da detecção de movimento
        pass
    
    def _trigger_capture(self):
        """Dispara captura de imagem"""
        self.last_trigger = time.time()
        # Notifica o sistema de captura
        self.capture_system.capture_image()
```

## **🎯 Parâmetros de Captura**

### **1. Configuração de Resolução e FPS**
```json
{
  "capture_params": {
    "resolution": {
      "width": 1920,
      "height": 1080,
      "auto_adjust": true
    },
    "fps": {
      "target": 30,
      "min": 15,
      "max": 60,
      "adaptive": true
    },
    "format": {
      "encoding": "JPEG",
      "quality": 85,
      "compression": "auto"
    },
    "buffer": {
      "size": 5,
      "strategy": "circular"
    }
  }
}
```

### **2. Implementação do Capture Manager**
```python
class CaptureManager:
    def __init__(self, source_config, capture_params):
        self.source_config = source_config
        self.capture_params = capture_params
        self.capture_device = None
        self.image_buffer = []
        
    def initialize_capture(self):
        """Inicializa dispositivo de captura"""
        if self.source_config["source_type"] == "usb_camera":
            self.capture_device = cv2.VideoCapture(
                self.source_config["config"]["device_id"]
            )
            
            # Configura resolução
            width = self.capture_params["resolution"]["width"]
            height = self.capture_params["resolution"]["height"]
            self.capture_device.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.capture_device.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            
            # Configura FPS
            fps = self.capture_params["fps"]["target"]
            self.capture_device.set(cv2.CAP_PROP_FPS, fps)
    
    def capture_image(self):
        """Captura uma imagem"""
        if self.capture_device and self.capture_device.isOpened():
            ret, frame = self.capture_device.read()
            if ret:
                # Processa imagem conforme parâmetros
                processed_frame = self._process_frame(frame)
                
                # Adiciona ao buffer
                self._add_to_buffer(processed_frame)
                
                return processed_frame
        return None
    
    def _process_frame(self, frame):
        """Processa frame conforme configuração"""
        # Redimensiona se necessário
        target_width = self.capture_params["resolution"]["width"]
        target_height = self.capture_params["resolution"]["height"]
        
        if frame.shape[1] != target_width or frame.shape[0] != target_height:
            frame = cv2.resize(frame, (target_width, target_height))
        
        # Converte formato se necessário
        if self.capture_params["format"]["encoding"] == "JPEG":
            # Converte para JPEG
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 
                          self.capture_params["format"]["quality"]]
            _, jpeg_data = cv2.imencode('.jpg', frame, encode_param)
            return jpeg_data.tobytes()
        
        return frame
```

## **🔧 Configuração via Interface Web Local**

### **1. Endpoint de Configuração**
```http
# Obter configuração atual
GET /api/machine/config/

# Atualizar configuração
PUT /api/machine/config/
{
  "source": {
    "source_type": "usb_camera",
    "config": {...}
  },
  "trigger": {
    "trigger_type": "continuous",
    "config": {...}
  },
  "capture_params": {...}
}

# Testar configuração
POST /api/machine/config/test/
{
  "config_section": "source"  // "source", "trigger", "capture"
}
```

### **2. Interface Web Local**
```python
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/config')
def config_page():
    """Página de configuração local"""
    return render_template('config.html', 
                         source_config=source_config,
                         trigger_config=trigger_config,
                         capture_params=capture_params)

@app.route('/api/machine/config/', methods=['GET'])
def get_config():
    """Retorna configuração atual"""
    return jsonify({
        "source": source_config.get_config(),
        "trigger": trigger_config.get_config(),
        "capture_params": capture_params.get_config()
    })

@app.route('/api/machine/config/', methods=['PUT'])
def update_config():
    """Atualiza configuração"""
    new_config = request.json
    
    # Valida configuração
    if not _validate_config(new_config):
        return jsonify({"error": "Invalid configuration"}), 400
    
    # Aplica configuração
    source_config.update(new_config["source"])
    trigger_config.update(new_config["trigger"])
    capture_params.update(new_config["capture_params"])
    
    # Reinicia sistemas se necessário
    _restart_systems_if_needed(new_config)
    
    return jsonify({"status": "Configuration updated successfully"})
```

## **📁 Estrutura de Arquivos da VM**

```
vm_flask/
├── config/
│   ├── source.json          # Configuração de source
│   ├── trigger.json         # Configuração de trigger
│   ├── capture.json         # Parâmetros de captura
│   └── machine.json         # Configuração geral da máquina
├── src/
│   ├── source_manager.py    # Gerenciador de source
│   ├── trigger_controller.py # Controlador de trigger
│   ├── capture_manager.py   # Gerenciador de captura
│   └── config_manager.py    # Gerenciador de configuração
├── web_interface/
│   ├── templates/
│   │   └── config.html      # Interface de configuração
│   └── static/
│       └── config.js        # JavaScript da interface
└── main.py                  # Aplicação principal
```

## **🚀 Auto-start e Persistência**

### **1. Sistema de Auto-start**
```python
class AutoStartManager:
    def __init__(self):
        self.config_file = "config/autostart.json"
        self.load_config()
    
    def load_config(self):
        """Carrega configuração de auto-start"""
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = self._default_config()
            self.save_config()
    
    def _default_config(self):
        """Configuração padrão de auto-start"""
        return {
            "enabled": True,
            "startup_delay": 5,
            "auto_reconnect": True,
            "health_check_interval": 30,
            "restart_on_failure": True,
            "max_restart_attempts": 3
        }
    
    def start_machine(self):
        """Inicia a máquina automaticamente"""
        if not self.config["enabled"]:
            return
        
        # Aguarda delay de startup
        time.sleep(self.config["startup_delay"])
        
        # Inicializa sistemas
        self._initialize_systems()
        
        # Inicia loop principal
        self._main_loop()
    
    def _initialize_systems(self):
        """Inicializa todos os sistemas"""
        # Source
        self.source_manager.initialize()
        
        # Trigger
        self.trigger_controller.start()
        
        # Capture
        self.capture_manager.initialize_capture()
        
        # Orquestrador (se configurado)
        if self.orchestrator_config:
            self._connect_to_orchestrator()
```

## **📊 Monitoramento de Configuração**

### **1. Status da Configuração**
```json
{
  "config_status": {
    "source": {
      "status": "active",
      "last_update": "2025-08-13T20:10:00Z",
      "health": "good",
      "current_config": {...}
    },
    "trigger": {
      "status": "running",
      "last_update": "2025-08-13T20:10:00Z",
      "health": "good",
      "current_config": {...}
    },
    "capture_params": {
      "status": "configured",
      "last_update": "2025-08-13T20:10:00Z",
      "health": "good",
      "current_config": {...}
    }
  }
}
```

### **2. Logs de Configuração**
```python
class ConfigLogger:
    def __init__(self):
        self.log_file = "logs/config_changes.log"
    
    def log_config_change(self, section, old_config, new_config):
        """Registra mudança de configuração"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "section": section,
            "old_config": old_config,
            "new_config": new_config,
            "user": "local"  # ou "orchestrator" se aplicável
        }
        
        with open(self.log_file, 'a') as f:
            json.dump(log_entry, f)
            f.write('\n')
```

## **✅ Benefícios da Configuração Local**

1. **🔄 Simplicidade**: VM é autônoma, não depende de ferramentas externas
2. **⚡ Performance**: Configuração carregada uma vez na inicialização
3. **🔒 Segurança**: Configurações sensíveis ficam na VM
4. **📱 Flexibilidade**: Interface web local para configuração
5. **🚀 Auto-start**: VM inicia automaticamente com configuração salva
6. **📊 Monitoramento**: Status e logs de configuração em tempo real
7. **🔄 Persistência**: Configurações sobrevivem a reinicializações

## **Próximos Passos**

1. [API Flask](./API-Flask.md) - Implementação das APIs de configuração
2. [Configuração de Source](./../04-Formato-Dados/Source-Config.md) - Schemas de configuração
3. [Fluxos de Configuração](./../06-Fluxos/Configuracao-Source.md) - Processos de configuração
4. [Exemplos de Configuração](./../07-Exemplos/Configuracao-Source.md) - Casos práticos
