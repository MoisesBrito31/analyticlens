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
- `GET /api/error` - Informações de erro

## 🧪 **Testes**

### **Teste Automatizado**
```bash
python test_vm.py
```

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
