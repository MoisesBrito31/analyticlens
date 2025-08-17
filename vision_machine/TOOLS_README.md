# 🛠️ Sistema de Ferramentas da Vision Machine

## 📋 **Visão Geral**

O sistema de ferramentas da Vision Machine é uma arquitetura modular que permite criar pipelines de inspeção personalizados através de configuração JSON. Cada ferramenta processa imagens de forma independente e pode referenciar resultados de ferramentas anteriores.

## 🏗️ **Arquitetura**

### **Hierarquia de Classes**
```
BaseTool (abstrata)
├── GrayscaleTool (filtro)
├── BlobTool (análise)
└── MathTool (matemática)
```

### **Fluxo de Processamento**
1. **InspectionProcessor** coordena a execução sequencial
2. **Cache de imagens** evita reprocessamento desnecessário
3. **Referências entre ferramentas** permitem operações matemáticas
4. **Medição de tempo** para cada ferramenta e inspeção completa

## 🔧 **Tipos de Ferramentas**

### **1. Ferramentas de Filtro (`filter`)**
- **Propósito**: Transformam a imagem para uso posterior
- **Exemplo**: `GrayscaleTool` - converte para escala de cinza
- **Característica**: Modificam a imagem e armazenam no cache

### **2. Ferramentas de Análise (`analysis`)**
- **Propósito**: Extraem informações e métricas da imagem
- **Exemplo**: `BlobTool` - detecta e analisa blobs
- **Característica**: Não modificam a imagem, apenas analisam

### **3. Ferramentas Matemáticas (`math`)**
- **Propósito**: Realizam cálculos sobre resultados de outras ferramentas
- **Exemplo**: `MathTool` - operações matemáticas e fórmulas customizadas
- **Característica**: Operam sobre dados, não sobre imagens

## 📝 **Configuração das Ferramentas**

### **Estrutura Base**
```json
{
  "tools": [
    {
      "id": 1,
      "name": "nome_da_ferramenta",
      "type": "tipo_da_ferramenta",
      "ROI": {"x": 0, "y": 0, "w": 100, "h": 100},
      "inspec_pass_fail": true,
      "reference_tool_id": null
    }
  ]
}
```

### **Campos Comuns**
- **`id`**: Identificador único da ferramenta (obrigatório)
- **`name`**: Nome descritivo da ferramenta
- **`type`**: Tipo da ferramenta (`grayscale`, `blob`, `math`)
- **`ROI`**: Região de interesse para processamento
- **`inspec_pass_fail`**: Se os testes internos afetam o resultado geral
- **`reference_tool_id`**: ID da ferramenta cujo resultado será usado como referência

## 🎯 **Ferramentas Disponíveis**

### **1. GrayscaleTool**
**Tipo**: `grayscale` (filtro)

**Parâmetros**:
- `method`: Método de conversão (`luminance`, `average`, `weighted`)
- `normalize`: Se deve normalizar a imagem (`true`/`false`)

**Exemplo**:
```json
{
  "id": 1,
  "name": "grayscale_filter",
  "type": "grayscale",
  "ROI": {"x": 0, "y": 0, "w": 640, "h": 480},
  "method": "luminance",
  "normalize": true,
  "inspec_pass_fail": false
}
```

**Resultado**:
```json
{
  "tool_id": 1,
  "tool_name": "grayscale_filter",
  "tool_type": "grayscale",
  "processing_time_ms": 1.23,
  "image_modified": true,
  "status": "success"
}
```

### **2. BlobTool**
**Tipo**: `blob` (análise)

**Parâmetros**:
- `th_min`/`th_max`: Limites do threshold (0-255)
- `area_min`/`area_max`: Limites de área dos blobs
- `test_total_area_min`/`test_total_area_max`: Limites para teste de área total
- `test_blob_count_min`/`test_blob_count_max`: Limites para teste de contagem
- `total_area_test`: Se deve executar teste de área total
- `blob_count_test`: Se deve executar teste de contagem

**Exemplo**:
```json
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
```

**Resultado**:
```json
{
  "tool_id": 2,
  "tool_name": "blob_1",
  "tool_type": "blob",
  "processing_time_ms": 2.45,
  "blobs": [
    {
      "area": 2674.5,
      "centroid": [23, 26],
      "bounding_box": [0, 0, 76, 80]
    }
  ],
  "blob_count": 5,
  "total_area": 3892.5,
  "roi_area": 360960.0,
  "test_results": {
    "total_area_test": {
      "passed": false,
      "min": 50.0,
      "max": 100.0,
      "actual": 3892.5
    },
    "blob_count_test": {
      "passed": true,
      "min": 4,
      "max": 5,
      "actual": 5
    },
    "overall_pass": false
  },
  "pass_fail": false
}
```

### **3. MathTool**
**Tipo**: `math` (matemática)

**Parâmetros**:
- `operation`: Operação matemática (`area_ratio`, `blob_density`, `custom_formula`)
- `reference_tool_id`: ID da ferramenta de referência
- `custom_formula`: Fórmula customizada (quando `operation` é `custom_formula`)

**Exemplo**:
```json
{
  "id": 3,
  "name": "area_ratio_calc",
  "type": "math",
  "ROI": {"x": 0, "y": 0, "w": 640, "h": 480},
  "operation": "area_ratio",
  "reference_tool_id": 2,
  "inspec_pass_fail": true
}
```

**Resultado**:
```json
{
  "tool_id": 3,
  "tool_name": "area_ratio_calc",
  "tool_type": "math",
  "processing_time_ms": 0.12,
  "operation": "area_ratio",
  "result": 0.0108,
  "pass_fail": true,
  "status": "success"
}
```

## 🚀 **Como Usar**

### **1. Configuração no vm_config.json**
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

### **2. Execução Automática**
```bash
cd vision_machine
python vm.py
```

### **3. Atualização Dinâmica via API**
```bash
# GET - Obter configuração atual
curl http://localhost:5000/api/inspection_config

# PUT - Atualizar configuração
curl -X PUT http://localhost:5000/api/inspection_config \
  -H "Content-Type: application/json" \
  -d @nova_config.json
```

## 📊 **Estrutura dos Resultados**

### **Resultado da Inspeção Completa**
```json
{
  "inspection_summary": {
    "total_processing_time_ms": 15.67,
    "tools_processing_time_ms": 12.34,
    "overhead_time_ms": 3.33,
    "overall_pass": false,
    "timestamp": "2025-08-17 02:09:03"
  },
  "tool_results": [
    // Resultados individuais de cada ferramenta
  ],
  "final_image": "base64_encoded_image_data"
}
```

### **Campos WebSocket**
- **`time`**: Tempo total de processamento da inspeção
- **`tools`**: Configuração JSON das ferramentas
- **`result`**: Lista de resultados de todas as ferramentas

## 🔍 **Debugging e Troubleshooting**

### **Logs de Processamento**
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

### **Problemas Comuns**
1. **Erro de serialização JSON**: Arrays numpy não são serializáveis
2. **Incompatibilidade de canais**: Imagens 2-channel vs 3-channel
3. **ROI fora dos limites**: Verificar coordenadas do ROI
4. **Configuração não atualizada**: Recriar InspectionProcessor

### **Validação de Configuração**
```python
# Cada ferramenta implementa validate_config()
if not tool.validate_config():
    print(f"❌ Configuração inválida para {tool.name}")
```

## 🎯 **Otimizações Implementadas**

### **1. Cache de Imagens Processadas**
- Ferramentas de filtro armazenam imagens processadas
- Ferramentas subsequentes reutilizam imagens já processadas
- Evita reprocessamento desnecessário

### **2. Pipeline Otimizado**
```
GrayscaleTool → [Cache] → BlobTool
     ↓              ↓         ↓
  Processa    Armazena   Reutiliza
```

### **3. Medição de Tempo**
- Tempo individual de cada ferramenta
- Tempo total da inspeção
- Overhead de processamento

## 🔮 **Próximos Passos**

### **Ferramentas Planejadas**
- **Edge Detection**: Detecção de bordas
- **Color Analysis**: Análise de cores
- **Pattern Matching**: Correspondência de padrões
- **OCR**: Reconhecimento de texto

### **Melhorias Técnicas**
- **Paralelização**: Execução paralela de ferramentas independentes
- **GPU Acceleration**: Uso de CUDA para processamento
- **Machine Learning**: Integração com modelos ML
- **Plugin System**: Sistema de plugins para ferramentas customizadas

---

## 📞 **Suporte**

Para dúvidas ou problemas com o sistema de ferramentas:
1. Verifique os logs de processamento
2. Valide a configuração JSON
3. Teste com `test_tools.py`
4. Use `test_user_vm.py` para testes manuais
