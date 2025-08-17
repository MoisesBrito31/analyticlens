# 🛠️ Sistema de Ferramentas da Vision Machine - Guia Completo

> 📖 **Projeto Principal**: [analyticLens - README Geral](../../README.md)

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

---

# 🎮 **Comandos da API para Gerenciamento de Tools**

## 📡 **Endpoint Principal**

Todos os comandos de tools são executados através do endpoint:
```
POST /api/control
```

## 🔧 **Comando config_tool**

### **Descrição**
Atualiza ou adiciona uma ferramenta de inspeção na Vision Machine em tempo real.

### **Formato da Requisição**
```json
{
  "command": "config_tool",
  "params": {
    "id": 1,
    "name": "grayscale_filter",
    "type": "grayscale",
    "ROI": {
      "x": 0,
      "y": 0,
      "w": 752,
      "h": 480
    },
    "method": "luminance",
    "normalize": true,
    "inspec_pass_fail": false
  }
}
```

### **Comportamento**

#### **1. Atualização de Tool Existente**
Se uma tool com o mesmo `id` e `name` já existir na configuração, ela será **atualizada** com os novos parâmetros.

**Exemplo de atualização:**
```json
{
  "command": "config_tool",
  "params": {
    "id": 1,
    "name": "grayscale_filter",
    "ROI": {
      "x": 50,    // Mudando posição X
      "y": 50,    // Mudando posição Y
      "w": 700,   // Mudando largura
      "h": 400    // Mudando altura
    }
  }
}
```

#### **2. Adição de Nova Tool**
Se não existir uma tool com o mesmo `id` e `name`, uma nova tool será **adicionada** ao final da fila de tools.

**Exemplo de nova tool:**
```json
{
  "command": "config_tool",
  "params": {
    "id": 999,           // Será substituído por ID único
    "name": "math_tool", // Nome único
    "type": "math",
    "operation": "add",
    "value": 50
  }
}
```

**Nota:** Se o `id` fornecido já existir, um novo ID único será gerado automaticamente.

### **Resposta da API**

#### **Sucesso (200)**
```json
{
  "success": true,
  "tool_id": 1,
  "tool_name": "grayscale_filter",
  "action": "updated",  // "updated" ou "added"
  "total_tools": 3
}
```

#### **Erro (400/500)**
```json
{
  "success": false,
  "error": "Mensagem de erro descritiva"
}
```

### **Ações Automáticas**
Após executar o comando `config_tool`, a VM automaticamente:

1. ✅ **Valida** a configuração da tool
2. ✅ **Atualiza** ou **adiciona** a tool na configuração
3. ✅ **Recria** o processador de inspeção com a nova configuração
4. ✅ **Salva** a configuração no arquivo JSON
5. ✅ **Aplica** a nova configuração para inspeções atuais

## 🗑️ **Comando delete_tool**

### **Descrição**
Remove uma ferramenta de inspeção pelo ID.

### **Formato da Requisição**
```json
{
  "command": "delete_tool",
  "params": {
    "id": 2
  }
}
```

### **Parâmetros**
- **id**: ID da tool a ser removida (inteiro obrigatório)

### **Comportamento**
- **Tool Encontrada**: Remove a tool e recria o processador
- **Tool Inexistente**: Retorna erro 500 com mensagem descritiva
- **Parâmetros Inválidos**: Retorna erro 400 com validação
- **Configuração**: Salva automaticamente após remoção

### **Resposta da API**

#### **Sucesso (200)**
```json
{
  "success": true,
  "tool_id": 2,
  "tool_name": "blob_1",
  "action": "deleted",
  "total_tools": 1
}
```

#### **Erro (400/500)**
```json
{
  "success": false,
  "error": "Mensagem de erro descritiva"
}
```

### **Ações Automáticas**
Após executar o comando `delete_tool`, a VM automaticamente:

1. ✅ **Valida** se a tool existe
2. ✅ **Remove** a tool da configuração
3. ✅ **Recria** o processador de inspeção (se houver tools restantes)
4. ✅ **Salva** a configuração no arquivo JSON
5. ✅ **Retorna** informações da operação

## 📋 **Exemplos de Uso**

### **Python**

```python
import requests

# Atualizar tool existente
response = requests.post("http://localhost:5000/api/control", json={
    "command": "config_tool",
    "params": {
        "id": 1,
        "name": "grayscale_filter",
        "ROI": {"x": 100, "y": 100, "w": 600, "h": 300}
    }
})

# Remover tool
response = requests.post("http://localhost:5000/api/control", json={
    "command": "delete_tool",
    "params": {"id": 2}
})

if response.status_code == 200:
    result = response.json()
    print(f"Tool {result['tool_name']} {result['action']} com sucesso!")
```

### **cURL**

```bash
# Atualizar tool existente
curl -X POST http://localhost:5000/api/control \
  -H "Content-Type: application/json" \
  -d '{
    "command": "config_tool",
    "params": {
      "id": 1,
      "name": "grayscale_filter",
      "ROI": {"x": 100, "y": 100, "w": 600, "h": 300}
    }
  }'

# Remover tool
curl -X POST http://localhost:5000/api/control \
  -H "Content-Type: application/json" \
  -d '{
    "command": "delete_tool",
    "params": {"id": 2}
  }'
```

## ⚠️ **Validações e Tratamento de Erros**

### **Validações Implementadas**

#### **config_tool**
- ✅ Presença dos campos obrigatórios (`id` e `name`)
- ✅ Estrutura da configuração da tool
- ✅ Compatibilidade com o sistema de ferramentas
- ✅ Integridade da configuração geral

#### **delete_tool**
- ✅ ID da tool deve ser fornecido
- ✅ ID deve ser um número inteiro válido
- ✅ Tool deve existir na configuração
- ✅ Lista de tools não pode estar vazia

### **Tratamento de Erros**

#### **Erro 400: Parâmetros Inválidos**
- Campos obrigatórios ausentes
- Formato de dados incorreto
- Tipos de dados inválidos

#### **Erro 500: Erro Interno**
- Falha ao recriar processador de ferramentas
- Erro ao salvar configuração
- Problemas com sistema de ferramentas
- Tool não encontrada para remoção

## 📝 **Logs e Debugging**

### **Logs Gerados**

#### **config_tool**
```
🔧 Comando config_tool recebido
🔄 Atualizando tool existente: grayscale_filter (ID: 1)
✅ Tool grayscale_filter atualizada com sucesso
✅ Processador de ferramentas recriado com 2 ferramentas
✅ Configuração de tool grayscale_filter atualizada e salva
```

#### **delete_tool**
```
🗑️ Comando delete_tool recebido
🗑️ Tool removida: blob_1 (ID: 2)
✅ Processador de ferramentas recriado com 1 ferramenta
✅ Tool blob_1 removida e configuração salva
```

### **Informações de Debug**
- **Status da VM**: Verificação de conectividade
- **Configurações**: Detalhes das tools testadas
- **Respostas da API**: Status codes e mensagens
- **Tempos de Processamento**: Performance das ferramentas

---

# 🔍 **Explicação Profunda dos Parâmetros das Tools**

## 📐 **Parâmetros Comuns a Todas as Tools**

### **`id` (Obrigatório)**
- **Tipo**: Integer
- **Descrição**: Identificador único da ferramenta
- **Valores**: Qualquer número inteiro positivo
- **Exemplo**: `1`, `2`, `100`
- **Nota**: Deve ser único dentro da configuração

### **`name` (Obrigatório)**
- **Tipo**: String
- **Descrição**: Nome descritivo da ferramenta
- **Valores**: Qualquer string válida
- **Exemplo**: `"grayscale_filter"`, `"blob_detector"`, `"area_calculator"`
- **Nota**: Deve ser único dentro da configuração

### **`type` (Obrigatório)**
- **Tipo**: String
- **Descrição**: Tipo da ferramenta
- **Valores**: `"grayscale"`, `"blob"`, `"math"`
- **Exemplo**: `"grayscale"`
- **Nota**: Determina a classe da ferramenta a ser instanciada

### **`ROI` (Obrigatório)**
- **Tipo**: Object
- **Descrição**: Região de interesse para processamento
- **Estrutura**: `{"x": 0, "y": 0, "w": 100, "h": 100}`

#### **Subparâmetros do ROI:**
- **`x`**: Posição X do canto superior esquerdo (pixels)
- **`y`**: Posição Y do canto superior esquerdo (pixels)
- **`w`**: Largura da região (pixels)
- **`h`**: Altura da região (pixels)

**Exemplo**: `{"x": 50, "y": 100, "w": 200, "h": 150}`

### **`inspec_pass_fail` (Opcional)**
- **Tipo**: Boolean
- **Descrição**: Se os testes internos afetam o resultado geral da inspeção
- **Valores**: `true` ou `false`
- **Padrão**: `false`
- **Exemplo**: `true`
- **Nota**: Tools com `true` podem fazer a inspeção falhar

### **`reference_tool_id` (Opcional)**
- **Tipo**: Integer ou null
- **Descrição**: ID da ferramenta cujo resultado será usado como referência
- **Valores**: ID de ferramenta existente ou `null`
- **Padrão**: `null`
- **Exemplo**: `2`
- **Nota**: Usado principalmente por ferramentas matemáticas

## 🎨 **Parâmetros Específicos da GrayscaleTool**

### **`method` (Obrigatório)**
- **Tipo**: String
- **Descrição**: Método de conversão para escala de cinza
- **Valores**: `"luminance"`, `"average"`, `"weighted"`
- **Padrão**: `"luminance"`

#### **Métodos Disponíveis:**

##### **`"luminance"`**
- **Fórmula**: `0.299 * R + 0.587 * G + 0.114 * B`
- **Características**: 
  - Mais próximo da percepção humana
  - Verde tem peso maior (58.7%)
  - Azul tem peso menor (11.4%)
- **Uso**: Padrão para inspeção visual
- **Exemplo**: `"method": "luminance"`

##### **`"average"`**
- **Fórmula**: `(R + G + B) / 3`
- **Características**:
  - Simples e rápido
  - Todos os canais têm peso igual
  - Pode não representar bem a luminosidade
- **Uso**: Processamento rápido quando precisão não é crítica
- **Exemplo**: `"method": "average"`

##### **`"weighted"`**
- **Fórmula**: `0.2126 * R + 0.7152 * G + 0.0722 * B`
- **Características**:
  - Baseado no padrão sRGB
  - Verde tem peso ainda maior (71.52%)
  - Azul tem peso ainda menor (7.22%)
- **Uso**: Processamento de imagens sRGB
- **Exemplo**: `"method": "weighted"`

### **`normalize` (Opcional)**
- **Tipo**: Boolean
- **Descrição**: Se deve normalizar a imagem após conversão
- **Valores**: `true` ou `false`
- **Padrão**: `false`

#### **Comportamento:**
- **`true`**: Aplica normalização para melhorar contraste
- **`false`**: Mantém valores originais
- **Exemplo**: `"normalize": true`

## 🔍 **Parâmetros Específicos da BlobTool**

### **`th_min` e `th_max` (Obrigatórios)**
- **Tipo**: Integer
- **Descrição**: Limites do threshold para detecção de blobs
- **Valores**: 0 a 255
- **Padrão**: `th_min: 0`, `th_max: 255`

#### **Comportamento:**
- **`th_min`**: Valor mínimo para considerar pixel como blob
- **`th_max`**: Valor máximo para considerar pixel como blob
- **Exemplo**: `"th_min": 130, "th_max": 255`
- **Nota**: Pixels com valor entre `th_min` e `th_max` são considerados blobs

### **`area_min` e `area_max` (Obrigatórios)**
- **Tipo**: Float
- **Descrição**: Limites de área dos blobs individuais
- **Valores**: Qualquer número positivo
- **Padrão**: `area_min: 0`, `area_max: inf`

#### **Comportamento:**
- **`area_min`**: Área mínima para considerar blob válido
- **`area_max`**: Área máxima para considerar blob válido
- **Exemplo**: `"area_min": 100, "area_max": 1000`
- **Nota**: Blobs fora desses limites são ignorados

### **`test_total_area_min` e `test_total_area_max` (Opcionais)**
- **Tipo**: Float
- **Descrição**: Limites para teste de área total de todos os blobs
- **Valores**: Qualquer número positivo
- **Padrão**: `null` (teste desabilitado)

#### **Comportamento:**
- **`test_total_area_min`**: Área total mínima aceitável
- **`test_total_area_max`**: Área total máxima aceitável
- **Exemplo**: `"test_total_area_min": 50, "test_total_area_max": 100`
- **Nota**: Só funciona se `total_area_test: true`

### **`test_blob_count_min` e `test_blob_count_max` (Opcionais)**
- **Tipo**: Integer
- **Descrição**: Limites para teste de contagem de blobs
- **Valores**: Qualquer número inteiro positivo
- **Padrão**: `null` (teste desabilitado)

#### **Comportamento:**
- **`test_blob_count_min`**: Número mínimo de blobs aceitável
- **`test_blob_count_max`**: Número máximo de blobs aceitável
- **Exemplo**: `"test_blob_count_min": 4, "test_blob_count_max": 5`
- **Nota**: Só funciona se `blob_count_test: true`

### **`total_area_test` (Opcional)**
- **Tipo**: Boolean
- **Descrição**: Se deve executar teste de área total
- **Valores**: `true` ou `false`
- **Padrão**: `false`

#### **Comportamento:**
- **`true`**: Executa teste de área total
- **`false`**: Ignora teste de área total
- **Exemplo**: `"total_area_test": true`
- **Nota**: Requer `test_total_area_min` e `test_total_area_max`

### **`blob_count_test` (Opcional)**
- **Tipo**: Boolean
- **Descrição**: Se deve executar teste de contagem de blobs
- **Valores**: `true` ou `false`
- **Padrão**: `false`

#### **Comportamento:**
- **`true`**: Executa teste de contagem
- **`false`**: Ignora teste de contagem
- **Exemplo**: `"blob_count_test": true`
- **Nota**: Requer `test_blob_count_min` e `test_blob_count_max`

## 🧮 **Parâmetros Específicos da MathTool**

### **`operation` (Obrigatório)**
- **Tipo**: String
- **Descrição**: Tipo de operação matemática a ser executada
- **Valores**: `"area_ratio"`, `"blob_density"`, `"custom_formula"`
- **Padrão**: Nenhum (obrigatório)

#### **Operações Disponíveis:**

##### **`"area_ratio"`**
- **Descrição**: Calcula a razão entre área de blobs e área total do ROI
- **Fórmula**: `total_blob_area / roi_area`
- **Requisitos**: `reference_tool_id` deve apontar para uma BlobTool
- **Resultado**: Valor entre 0 e 1
- **Exemplo**: `"operation": "area_ratio"`

##### **`"blob_density"`**
- **Descrição**: Calcula a densidade de blobs por área
- **Fórmula**: `blob_count / roi_area`
- **Requisitos**: `reference_tool_id` deve apontar para uma BlobTool
- **Resultado**: Blobs por pixel²
- **Exemplo**: `"operation": "blob_density"`

##### **`"custom_formula"`**
- **Descrição**: Executa fórmula customizada
- **Fórmula**: Definida em `custom_formula`
- **Requisitos**: `custom_formula` deve ser definida
- **Resultado**: Resultado da fórmula customizada
- **Exemplo**: `"operation": "custom_formula"`

### **`custom_formula` (Opcional)**
- **Tipo**: String
- **Descrição**: Fórmula customizada para operação matemática
- **Valores**: Expressão matemática válida
- **Padrão**: `null`
- **Exemplo**: `"custom_formula": "blob_count * 2 + total_area / 100"`

#### **Variáveis Disponíveis:**
- **`blob_count`**: Número de blobs da ferramenta de referência
- **`total_area`**: Área total dos blobs da ferramenta de referência
- **`roi_area`**: Área da região de interesse
- **`blob_areas`**: Lista de áreas individuais dos blobs

#### **Operadores Suportados:**
- **Aritméticos**: `+`, `-`, `*`, `/`, `%`
- **Comparação**: `==`, `!=`, `>`, `<`, `>=`, `<=`
- **Lógicos**: `and`, `or`, `not`
- **Parênteses**: `()`

## 📊 **Exemplos de Configuração Completa**

### **Pipeline Básico: Grayscale + Blob**
```json
{
  "tools": [
    {
      "id": 1,
      "name": "grayscale_converter",
      "type": "grayscale",
      "ROI": {"x": 0, "y": 0, "w": 640, "h": 480},
      "method": "luminance",
      "normalize": true,
      "inspec_pass_fail": false
    },
    {
      "id": 2,
      "name": "defect_detector",
      "type": "blob",
      "ROI": {"x": 100, "y": 100, "w": 200, "h": 200},
      "th_min": 150,
      "th_max": 255,
      "area_min": 50,
      "area_max": 500,
      "test_total_area_min": 0,
      "test_total_area_max": 1000,
      "test_blob_count_min": 0,
      "test_blob_count_max": 5,
      "total_area_test": true,
      "blob_count_test": true,
      "inspec_pass_fail": true
    }
  ]
}
```

### **Pipeline Avançado: Grayscale + Blob + Math**
```json
{
  "tools": [
    {
      "id": 1,
      "name": "grayscale_converter",
      "type": "grayscale",
      "ROI": {"x": 0, "y": 0, "w": 640, "h": 480},
      "method": "weighted",
      "normalize": false,
      "inspec_pass_fail": false
    },
    {
      "id": 2,
      "name": "defect_detector",
      "type": "blob",
      "ROI": {"x": 50, "y": 50, "w": 300, "h": 300},
      "th_min": 120,
      "th_max": 255,
      "area_min": 25,
      "area_max": 1000,
      "test_total_area_min": 0,
      "test_total_area_max": 5000,
      "test_blob_count_min": 0,
      "test_blob_count_max": 10,
      "total_area_test": true,
      "blob_count_test": true,
      "inspec_pass_fail": true
    },
    {
      "id": 3,
      "name": "quality_calculator",
      "type": "math",
      "ROI": {"x": 0, "y": 0, "w": 640, "h": 480},
      "operation": "area_ratio",
      "reference_tool_id": 2,
      "inspec_pass_fail": true
    }
  ]
}
```

### **Pipeline com Fórmula Customizada**
```json
{
  "tools": [
    {
      "id": 1,
      "name": "grayscale_converter",
      "type": "grayscale",
      "ROI": {"x": 0, "y": 0, "w": 640, "h": 480},
      "method": "luminance",
      "normalize": true,
      "inspec_pass_fail": false
    },
    {
      "id": 2,
      "name": "defect_detector",
      "type": "blob",
      "ROI": {"x": 0, "y": 0, "w": 640, "h": 480},
      "th_min": 100,
      "th_max": 255,
      "area_min": 10,
      "area_max": 1000,
      "test_total_area_min": 0,
      "test_total_area_max": 10000,
      "test_blob_count_min": 0,
      "test_blob_count_max": 20,
      "total_area_test": true,
      "blob_count_test": true,
      "inspec_pass_fail": true
    },
    {
      "id": 3,
      "name": "custom_quality_score",
      "type": "math",
      "ROI": {"x": 0, "y": 0, "w": 640, "h": 480},
      "operation": "custom_formula",
      "reference_tool_id": 2,
      "custom_formula": "100 - (total_area / roi_area * 100) - (blob_count * 2)",
      "inspec_pass_fail": true
    }
  ]
}
```

## 🎯 **Dicas de Configuração**

### **1. Ordem das Ferramentas**
- **Ferramentas de filtro** devem vir primeiro
- **Ferramentas de análise** devem vir depois dos filtros
- **Ferramentas matemáticas** devem vir por último

### **2. Configuração de ROI**
- **ROI pequeno**: Processamento mais rápido, menos ruído
- **ROI grande**: Mais contexto, mas pode incluir ruído
- **ROI sobreposto**: Pode ser útil para análise em diferentes escalas

### **3. Thresholds para Blob Detection**
- **`th_min` baixo**: Detecta mais objetos (pode incluir ruído)
- **`th_max` alto**: Detecta objetos mais claros
- **Teste com valores**: Use ferramentas de visualização para ajustar

### **4. Testes de Pass/Fail**
- **`inspec_pass_fail: false`**: Para ferramentas de pré-processamento
- **`inspec_pass_fail: true`**: Para ferramentas de decisão final
- **Testes múltiplos**: Combine área total e contagem para robustez

---

# 🧪 **Sistema de Testes**

## 📋 **Execução dos Testes**

### **Teste Completo**
```bash
# Na pasta vision_machine
python test_tools.py
```

### **Verificação Pré-Teste**
```bash
# Verificar se VM está rodando
curl http://localhost:5000/api/error

# Verificar configuração atual
curl http://localhost:5000/api/inspection_config
```

## 🔄 **Sistema de Backup/Restauração**

O sistema de testes implementa:
- ✅ **Backup automático** da configuração atual
- ✅ **Execução segura** dos testes
- ✅ **Restauração garantida** da configuração original
- ✅ **Isolamento total** dos testes

## 📊 **Resultados Esperados**

```
📈 Resumo: 4/4 testes passaram
🎉 Todos os testes passaram com sucesso!
```

---

# 🏁 **Conclusão**

Este guia completo cobre todos os aspectos do sistema de ferramentas da Vision Machine, incluindo:

1. **Configuração detalhada** de cada tipo de ferramenta
2. **Comandos da API** para gerenciamento dinâmico
3. **Explicação profunda** de todos os parâmetros
4. **Exemplos práticos** de configuração
5. **Sistema de testes** com backup/restauração
6. **Dicas e melhores práticas** para configuração

Com essas informações, você pode configurar, gerenciar e otimizar completamente o sistema de ferramentas para suas necessidades específicas de inspeção.
