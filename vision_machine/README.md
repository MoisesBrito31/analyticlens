# 🎯 Vision Machine (VM) - Sistema de Visão Computacional

> 📖 **Projeto Principal**: [analyticLens - README Geral](../../README.md)

## 📋 **Visão Geral**

A Vision Machine é um servidor Flask robusto para visão computacional que se comunica via REST API e WebSocket. O sistema oferece processamento de imagens em tempo real com configuração flexível de fontes de imagem e modos de operação.

## ✨ **Funcionalidades Principais**

### **🔧 Sistema de Ferramentas Modular**
- **Pipeline de Inspeção**: Configuração JSON para criar receitas de processamento
- **Ferramentas Disponíveis**: Grayscale (filtro), Blob (análise), Math (cálculos)
- **Execução Sequencial**: Processamento otimizado com cache de imagens
- **Referências entre Ferramentas**: Uma ferramenta pode usar resultados de outra

### **📷 Fontes de Imagem Flexíveis**
- **Pasta de Imagens**: Processamento de arquivos locais
- **Câmera Local**: Captura direta via OpenCV
- **Câmera IP**: Stream RTSP/HTTP
- **Câmera Raspberry Pi (Picamera2)**: Captura nativa via biblioteca Picamera2

### **⚡ Modos de Operação**
- **Contínuo**: Inspeção automática em intervalos configuráveis
- **Trigger**: Inspeção sob demanda via comando REST

### **🌐 Comunicação em Tempo Real**
- **REST API**: Controle e configuração
- **WebSocket**: Resultados de inspeção em tempo real
- **Eventos**: `inspection_result`, `test_result`

## 🏗️ **Arquitetura**

### **Componentes Principais**
```
VisionMachine (Core)
├── InspectionProcessor (Sistema de Ferramentas)
│   ├── BaseTool (Classe Abstrata)
│   ├── GrayscaleTool (Filtro)
│   ├── BlobTool (Análise)
│   └── MathTool (Matemática)
├── ImageSource (Fontes de Imagem)
├── TestModeProcessor (Processamento)
└── FlaskVisionServer (API + WebSocket)
```

### **Fluxo de Processamento**
1. **Captura**: Imagem da fonte configurada
2. **Pipeline**: Execução sequencial das ferramentas
3. **Cache**: Reutilização de imagens processadas
4. **Análise**: Resultados com métricas de tempo
5. **WebSocket**: Envio dos resultados em tempo real

## 🚀 **Início Rápido**

### **1. Instalação**
```bash
cd vision_machine
pip install -r requirements.txt
```

### **2. Configuração**
Edite `vm_config.json` para configurar:
- Fonte de imagem
- Modo de trigger
- Pipeline de ferramentas

Exemplo de configuração de fonte Picamera2:
```json
{
  "source_config": {
    "type": "picamera2",
    "resolution": [1280, 720]
  }
}
```

### **3. Execução**
```bash
python vm.py
```

### **4. Acesso**
- **API**: http://localhost:5000
- **WebSocket**: ws://localhost:5000

## 📷 Picamera2 (Raspberry Pi)

### Instalação no Raspberry Pi OS
```bash
sudo apt update && sudo apt install -y python3-picamera2
sudo usermod -aG video $USER  # reinicie a sessão após
```

### Configuração via API
```bash
curl -X PUT http://<IP_DA_VM>:5000/api/source_config \
  -H "Content-Type: application/json" \
  -d '{"type":"picamera2","resolution":[1280,720]}'
```

Observações:
- O tipo de fonte JSON é `picamera2` (igual ao nome da biblioteca).
- Um alias `camerapi2` é aceito temporariamente para retrocompatibilidade.
- A imagem é capturada em RGB e convertida internamente para BGR (OpenCV).

## 📚 **Documentação**

### **📖 Guias Principais**
- **[TOOLS_README.md](TOOLS_README.md)**: Sistema de ferramentas completo
- **[Protocolo/](Protocolo/)**: Especificações técnicas detalhadas
- **[modelagem/](modelagem/)**: Diagramas UML e arquiteturais

### **🔧 Ferramentas Disponíveis**
- **GrayscaleTool**: Conversão para escala de cinza
- **BlobTool**: Detecção e análise de blobs
- **LocateTool**: Localização de borda ao longo de seta; exporta referência/resultado/offset; pode realocar ROIs subsequentes
- **MathTool**: Operações matemáticas sobre resultados

### **📡 APIs Disponíveis**
- `GET/PUT /api/status` - Status da VM
- `POST /api/control` - Controle (start/stop/trigger)
- `GET/PUT /api/source_config` - Configuração da fonte
- `GET/PUT /api/trigger_config` - Configuração do trigger
- `GET/PUT /api/inspection_config` - Configuração das ferramentas
- `GET/PUT /api/logging_config` - Configuração de logging de resultados
- `GET /api/error` - Informações de erro

## 🧾 Sistema de Logging de Resultados

### 📋 **Visão Geral**
Sistema completo de logging de resultados de inspeção com armazenamento local, sincronização com orquestrador e interface de gerenciamento.

**Características principais:**
- ✅ **Logging local**: Arquivos `.alog` com formato binário otimizado
- ✅ **Buffer em memória**: Escrita assíncrona em lote para performance
- ✅ **Sincronização**: Upload automático para o orquestrador Django
- ✅ **Retenção inteligente**: Políticas `keep_last` e `keep_first`
- ✅ **Filtros**: Logging por política (`ALL`, `APPROVED`, `REJECTED`)
- ✅ **Interface web**: Gerenciamento via frontend Vue.js

### ⚙️ **Configuração**

#### **Arquivo de Configuração (vm_config.json)**
```json
{
  "logging": {
    "enabled": true,
    "mode": "keep_last",          
    "max_logs": 1000,
    "policy": "ALL",              
    "batch_size": 20,               
    "batch_ms": 500,
    "buffer_size": 0
  }
}
```

**Parâmetros:**
- `enabled`: Ativa/desativa o sistema de logging
- `mode`: `keep_last` (remove antigos) | `keep_first` (rejeita novos quando cheio)
- `max_logs`: Limite máximo de arquivos `.alog` (0 = sem limite)
- `policy`: `ALL` | `APPROVED` | `REJECTED` (filtro de resultados)
- `batch_size`: Quantidade de logs para flush do buffer
- `batch_ms`: Intervalo máximo (ms) para flush do buffer
- `buffer_size`: Tamanho atual do buffer (somente leitura)

#### **Configuração via API**
```bash
# Atualizar configuração
curl -X PUT http://localhost:5000/api/logging_config \
  -H 'Content-Type: application/json' \
  -d '{"enabled":true,"policy":"ALL","batch_size":10,"batch_ms":1000}'

# Consultar configuração atual
curl http://localhost:5000/api/logging_config
```

### 📡 **Endpoints da API**

#### **Configuração de Logging**
- `GET /api/logging_config` - Consultar configuração atual
- `PUT /api/logging_config` - Atualizar configuração

#### **Controle de Logs**
- `POST /api/control` com `{"command": "clear_logs"}` - Limpar logs do disco
- `POST /api/logs/sync` - Sincronizar logs com orquestrador

#### **Status da VM**
- `GET /api/status` inclui:
  - `logging_config`: Configuração atual
  - `logging_buffer_size`: Tamanho do buffer em memória
  - `logs_count`: Quantidade de arquivos `.alog` no disco

### 🗂️ **Formato do Arquivo .alog**

#### **Estrutura Binária**
```
┌─────────────┬─────────────┬─────────────┬─────────────┬─────────────┬─────────────┐
│ Magic (4B)  │ Version (4B)│ JSON Len(8B)│ JPEG Len(8B)│ JSON Data   │ JPEG Data   │
│ "ALOG"      │ uint32 BE   │ uint64 BE   │ uint64 BE   │ UTF-8       │ Binary      │
└─────────────┴─────────────┴─────────────┴─────────────┴─────────────┴─────────────┘
```

#### **Conteúdo do JSON**
```json
{
  "inspection_summary": {
    "frame": 42,
    "total_processing_time_ms": 15.67,
    "tools_count": 2,
    "approved_count": 1,
    "rejected_count": 1
  },
  "tools": [
    {
      "order_index": 0,
      "name": "grayscale_filter",
      "type": "grayscale",
      "ROI": {"shape": "rect", "rect": {"x": 0, "y": 0, "w": 640, "h": 480}},
      "inspec_pass_fail": false
    }
  ],
  "result": [
    {
      "order_index": 0,
      "name": "grayscale_filter",
      "type": "grayscale",
      "inspec_pass_fail": false,
      "processing_time_ms": 2.34
    }
  ],
  "aprovados": 1,
  "reprovados": 1,
  "frame": 42,
  "time": "15.67ms"
}
```

#### **Leitura em Python**
```python
import struct
import json
from datetime import datetime

def read_alog_file(filepath):
    """Lê um arquivo .alog e retorna JSON + imagem"""
    with open(filepath, 'rb') as f:
        # Ler cabeçalho
        magic = f.read(4)
        assert magic == b'ALOG', "Arquivo inválido"
        
        version = struct.unpack('>I', f.read(4))[0]
        json_len = struct.unpack('>Q', f.read(8))[0]
        jpeg_len = struct.unpack('>Q', f.read(8))[0]
        
        # Ler dados
        json_data = f.read(json_len)
        jpeg_data = f.read(jpeg_len) if jpeg_len > 0 else b''
        
        # Parse JSON
        result = json.loads(json_data.decode('utf-8'))
        
        return {
            'version': version,
            'json': result,
            'image': jpeg_data,
            'image_size': jpeg_len
        }

# Exemplo de uso
log_data = read_alog_file('logs/2025-01-15_14-30-25_abc123.alog')
print(f"Frame: {log_data['json']['frame']}")
print(f"Aprovados: {log_data['json']['aprovados']}")
```

### 🔄 **Sincronização com Orquestrador**

#### **Fluxo de Sincronização**
1. **Trigger**: Comando `sync_logs` via API ou interface web
2. **Upload**: VM envia arquivos `.alog` para Django via `POST /api/logs/upload`
3. **Processamento**: Django extrai imagem e salva no banco de dados
4. **Limpeza**: VM remove arquivos enviados com sucesso
5. **Atualização**: Frontend atualiza contadores e listas

#### **Comando de Sincronização**
```bash
# Via API da VM
curl -X POST http://localhost:5000/api/logs/sync \
  -H 'Content-Type: application/json' \
  -d '{"django_url": "http://localhost:8000"}'

# Via API do Orquestrador
curl -X POST http://localhost:8000/api/vms/{vm_id}/sync_logs
```

### 🧪 **Testes e Validação**

#### **Teste Automatizado**
```bash
# Executar teste completo de logging
python test_vm.py

# O teste inclui:
# 1. Backup da configuração atual
# 2. Habilitação do logging
# 3. Processamento de frames
# 4. Verificação de criação de .alog
# 5. Restauração da configuração original
```

#### **Teste Manual**
```bash
# 1. Habilitar logging
curl -X PUT http://localhost:5000/api/logging_config \
  -H 'Content-Type: application/json' \
  -d '{"enabled":true,"policy":"ALL","batch_size":2,"batch_ms":200}'

# 2. Iniciar inspeção contínua
curl -X PUT http://localhost:5000/api/trigger_config \
  -H 'Content-Type: application/json' \
  -d '{"type":"continuous","interval_ms":300}'

curl -X POST http://localhost:5000/api/control \
  -H 'Content-Type: application/json' \
  -d '{"command":"start_inspection","params":{}}'

# 3. Aguardar e verificar
sleep 5
curl http://localhost:5000/api/status | jq '.logs_count, .logging_buffer_size'

# 4. Verificar arquivos
ls -la logs/*.alog
```

### 📊 **Monitoramento e Métricas**

#### **Métricas Disponíveis**
- **`logs_count`**: Quantidade de arquivos `.alog` no disco
- **`logging_buffer_size`**: Tamanho atual do buffer em memória
- **`batch_size`**: Configuração de flush do buffer
- **`batch_ms`**: Intervalo de flush configurado

#### **Logs de Sistema**
```bash
# Logs da VM mostram atividade de logging
tail -f vision_machine.log | grep -i log

# Exemplo de saída:
# [INFO] Logging habilitado: policy=ALL, max_logs=1000
# [DEBUG] Buffer de logs: 5/20 itens
# [INFO] Flush de logs: 20 itens salvos em disco
# [DEBUG] Arquivo .alog criado: logs/2025-01-15_14-30-25_abc123.alog
```

### 🗂️ **Estrutura de Diretórios**

```
vision_machine/
├── logs/                          # Diretório de logs (criado automaticamente)
│   ├── 2025-01-15_14-30-25_abc123.alog
│   ├── 2025-01-15_14-30-26_def456.alog
│   └── ...
├── vm_config.json                 # Configuração da VM
├── vm.py                         # Servidor principal
└── requirements.txt              # Dependências
```

### ⚠️ **Considerações Importantes**

#### **Performance**
- **Buffer em memória**: Evita I/O síncrono durante inspeção
- **Escrita em lote**: Otimiza operações de disco
- **Compressão JPEG**: Reduz tamanho dos arquivos

#### **Armazenamento**
- **Retenção automática**: Remove logs antigos quando necessário
- **Limite configurável**: Evita esgotamento de espaço em disco
- **Sincronização**: Upload automático para orquestrador

#### **Recuperação**
- **Backup automático**: Configuração original preservada em testes
- **Rollback**: Restauração automática em caso de erro
- **Validação**: Verificação de integridade dos arquivos

### 🔧 **Troubleshooting**

#### **Problemas Comuns**

**1. Logs não sendo criados**
```bash
# Verificar se logging está habilitado
curl http://localhost:5000/api/logging_config | jq '.enabled'

# Verificar status da VM
curl http://localhost:5000/api/status | jq '.inspection_running'
```

**2. Buffer não fazendo flush**
```bash
# Verificar configuração do buffer
curl http://localhost:5000/api/logging_config | jq '.batch_size, .batch_ms'

# Forçar flush (reduzir batch_size temporariamente)
curl -X PUT http://localhost:5000/api/logging_config \
  -H 'Content-Type: application/json' \
  -d '{"batch_size":1,"batch_ms":100}'
```

**3. Sincronização falhando**
```bash
# Verificar conectividade com orquestrador
curl -X POST http://localhost:5000/api/logs/sync \
  -H 'Content-Type: application/json' \
  -d '{"django_url": "http://localhost:8000"}'

# Verificar logs da VM
tail -f vision_machine.log | grep -i sync
```

### 📈 **Próximas Melhorias**

- **Compressão**: Implementar compressão adicional dos arquivos
- **Indexação**: Índices para busca rápida por critérios
- **Métricas avançadas**: Estatísticas de performance e uso
- **Backup automático**: Sincronização com sistemas de backup
- **Alertas**: Notificações para problemas de armazenamento

## 🧪 **Testes**

### **Teste Automatizado**
```bash
python test_vm.py
```
O script inclui um teste de logging básico que habilita o recurso, processa frames e verifica a criação de `.alog`, restaurando as configurações anteriores ao final.

### **Teste Manual Interativo**
```bash
python test_user_vm.py
```

### **Teste das Ferramentas**
```bash
python test_tools.py
```

## ⚙️ **Configuração**

### **Exemplo de Pipeline de Ferramentas**
```json
{
  "inspection_config": {
    "tools": [
      {
        "id": 1,
        "name": "grayscale_filter",
        "type": "grayscale",
        "ROI": {"x": 0, "y": 0, "w": 640, "h": 480},
        "method": "luminance",
        "normalize": true,
        "inspec_pass_fail": false
      },
      {
        "id": 2,
        "name": "blob_1",
        "type": "blob",
        "ROI": {"x": 0, "y": 10, "w": 100, "h": 100},
        "th_max": 255,
        "th_min": 130,
        "area_min": 100,
        "area_max": 1000,
        "test_total_area_max": 100,
        "test_total_area_min": 50,
        "test_blob_count_max": 5,
        "test_blob_count_min": 4,
        "total_area_test": true,
        "blob_count_test": true,
        "inspec_pass_fail": true
      }
    ]
  }
}
```

## 🔍 **Monitoramento**

### **Logs em Tempo Real**
```
 Iniciando inspeção com 2 ferramentas...
   1️⃣ Processando grayscale_filter (ID: 1)...
   🔄 Usando imagem grayscale já processada para blob_1
   2️⃣ Processando blob_1 (ID: 2)...
   ✅ Pipeline funcionando corretamente
   📊 Grayscale: 1.23ms
   📊 Blob: 2.45ms
   🎯 Sem duplicação de processamento grayscale
```

### **Métricas de Performance**
- Tempo individual de cada ferramenta
- Tempo total da inspeção
- Overhead de processamento
- Cache hit/miss rates

## 🛠️ **Desenvolvimento**

### **Estrutura do Projeto**
```
vision_machine/
├── tools/                    # Sistema de ferramentas
│   ├── __init__.py
│   ├── base_tool.py         # Classe base abstrata
│   ├── grayscale_tool.py    # Ferramenta grayscale
│   ├── blob_tool.py         # Ferramenta blob
│   └── math_tool.py         # Ferramenta matemática
├── inspection_processor.py   # Processador principal
├── vm.py                    # VM principal
├── vm_config.json           # Configuração
└── test_*.py                # Scripts de teste
```

### **Adicionando Novas Ferramentas**
1. Herde de `BaseTool`
2. Implemente o método `process()`
3. Adicione validação em `validate_config()`
4. Registre no `InspectionProcessor`

## 🚧 **Limitações Atuais**

- ROI apenas retangular
- Validação básica de configuração
- Tratamento de erro via exceções
- Processamento sequencial (não paralelo)

## 🔮 **Roadmap**

### **Próximas Ferramentas**
- Edge Detection
- Color Analysis
- Pattern Matching
- OCR

### **Melhorias Técnicas**
- Paralelização de ferramentas independentes
- GPU acceleration
- Machine learning integration
- Plugin system

## 📞 **Suporte**

Para dúvidas ou problemas:
1. Verifique os logs da VM
2. Execute os scripts de teste
3. Consulte a documentação
4. Valide a configuração JSON

---

## 📊 **Status do Projeto**

- ✅ **Sistema de Ferramentas**: Implementado e testado
- ✅ **Trigger Config**: Modo contínuo e trigger
- ✅ **WebSocket**: Resultados em tempo real
- ✅ **API REST**: Controle completo
- ✅ **Cache de Imagens**: Otimização de pipeline
- ✅ **Medição de Tempo**: Performance monitoring
- 🔄 **Testes**: Cobertura completa
- 📚 **Documentação**: Atualizada

**🎯 Vision Machine v2.0 - Sistema de Ferramentas Completo**
