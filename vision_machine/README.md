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
- **MathTool**: Operações matemáticas sobre resultados

### **📡 APIs Disponíveis**
- `GET/PUT /api/status` - Status da VM
- `POST /api/control` - Controle (start/stop/trigger)
- `GET/PUT /api/source_config` - Configuração da fonte
- `GET/PUT /api/trigger_config` - Configuração do trigger
- `GET/PUT /api/inspection_config` - Configuração das ferramentas
- `GET/PUT /api/logging_config` - Configuração de logging de resultados
- `GET /api/error` - Informações de erro

## 🧾 Logging de Resultados (VM 11)

### Visão Geral
- Logging local em disco com escrita assíncrona em lote.
- Cada resultado é gravado em um único arquivo `.alog` contendo cabeçalho + JSON + JPEG.
- Retenção configurável: `keep_last` (remove antigos) ou `keep_first` (rejeita novos quando cheio).

### Configuração (vm_config.json)
Chave `logging` (também editável via `PUT /api/logging_config`):
```json
{
  "logging": {
    "enabled": true,
    "mode": "keep_last",          
    "max_logs": 1000,
    "policy": "ALL",              
    "batch_size": 20,               
    "batch_ms": 500                 
  }
}
```
- `enabled`: ativa/desativa logging
- `mode`: `keep_last`|`keep_first`
- `max_logs`: limite máximo de arquivos `.alog` (0 desativa persistência)
- `policy`: `ALL`|`APPROVED`|`REJECTED`
- `batch_size`/`batch_ms`: critérios de flush do buffer de RAM

### Endpoints
- `GET /api/logging_config` → retorna config e `buffer_size`
- `PUT /api/logging_config` → atualiza config
- `GET /api/status` inclui:
  - `logging_config`
  - `logging_buffer_size`
  - `logs_count` (quantidade de `.alog` no diretório)

### Operação
- A VM mantém um buffer de resultados em RAM; um worker assíncrono grava em lote.
- Imagem gravada em JPEG (qualidade 80); JSON sem o array da imagem.
- Diretório padrão dos logs: `./logs` (ao lado de `vm_config.json`).

### Formato do arquivo .alog
Estrutura binária:
- Magic: `ALOG` (4 bytes)
- Versão: `uint32` (big endian)
- JSON length: `uint64` (big endian)
- JPEG length: `uint64` (big endian)
- JSON bytes (UTF-8)
- JPEG bytes (opcional)

Leitura simples em Python:
```python
import struct, json

with open('logs/2025-09-12_12-00-00_<uuid>.alog','rb') as f:
    magic = f.read(4)
    assert magic == b'ALOG'
    version = struct.unpack('>I', f.read(4))[0]
    jlen = struct.unpack('>Q', f.read(8))[0]
    ilen = struct.unpack('>Q', f.read(8))[0]
    jbytes = f.read(jlen)
    ib = f.read(ilen) if ilen else b''
    data = json.loads(jbytes.decode('utf-8'))
```

### Teste Rápido
1. Habilite logging:
```bash
curl -X PUT http://localhost:5000/api/logging_config \
  -H 'Content-Type: application/json' \
  -d '{"enabled":true,"policy":"ALL","batch_size":2,"batch_ms":200}'
```
2. Configure trigger contínuo e inicie a inspeção:
```bash
curl -X PUT http://localhost:5000/api/trigger_config -H 'Content-Type: application/json' -d '{"type":"continuous","interval_ms":300}'
curl -X POST http://localhost:5000/api/control -H 'Content-Type: application/json' -d '{"command":"start_inspection","params":{}}'
```
3. Aguarde alguns segundos e valide o status:
```bash
curl http://localhost:5000/api/status | jq '.logs_count, .logging_buffer_size'
```
4. Arquivos `.alog` estarão em `vision_machine/logs`.

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
