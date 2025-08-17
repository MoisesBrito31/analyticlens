# Sistema de Testes de Tools - Vision Machine

> 📖 **Projeto Principal**: [analyticLens - README Geral](../../README.md)

## Visão Geral

O arquivo `test_tools.py` é o **único arquivo de teste** para o segmento de tools da aplicação. Ele implementa um sistema completo de testes com backup/restauração automática da configuração.

## 🚀 Características Principais

### ✅ **Sistema de Backup/Restauração**
- **Backup Automático**: Salva configuração atual antes dos testes
- **Restauração Garantida**: Restaura configuração original após testes
- **Segurança Total**: Nunca perde configurações originais

### 🧪 **Testes Integrados**
- **Processador de Ferramentas**: Testa funcionalidade básica
- **Comando config_tool**: Testa atualização e adição de tools
- **Comando delete_tool**: Testa remoção de tools
- **Tratamento de Erros**: Valida robustez dos comandos

### 🔄 **Execução Segura**
- **Isolamento**: Testes não afetam configuração de produção
- **Rollback Automático**: Restauração em caso de falha
- **Logs Detalhados**: Rastreamento completo de operações

## 📋 Como Executar

### Pré-requisitos
1. **VM Rodando**: Vision Machine deve estar ativa em `http://localhost:5000`
2. **Dependências**: `requests`, `cv2`, `numpy`, `inspection_processor`

### Execução Simples
```bash
# Na pasta vision_machine
python test_tools.py
```

### Execução com Verificação
```bash
# Verificar se VM está rodando
curl http://localhost:5000/api/error

# Executar testes
python test_tools.py
```

## 🧪 Testes Incluídos

### 1. **Processador de Ferramentas**
- ✅ Inicialização do processador
- ✅ Validação de ferramentas
- ✅ Processamento de imagem de teste
- ✅ Verificação de resultados

### 2. **Comando config_tool**
- ✅ Atualização de tool existente
- ✅ Adição de nova tool
- ✅ Verificação de configuração
- ✅ Geração de IDs únicos

### 3. **Comando delete_tool**
- ✅ Remoção de tool existente
- ✅ Tratamento de tool inexistente
- ✅ Verificação de configuração
- ✅ Validação de parâmetros

### 4. **Tratamento de Erros**
- ✅ Parâmetros ausentes
- ✅ Tipos de dados inválidos
- ✅ Validação de entrada
- ✅ Mensagens de erro apropriadas

## 🔄 Fluxo de Execução

```
🚀 Início dos Testes
    ↓
💾 Criar Backup da Configuração Atual
    ↓
🧪 Executar Todos os Testes
    ↓
🔄 Restaurar Configuração Original
    ↓
📊 Exibir Resultados
    ↓
🏁 Finalizar
```

## 📊 Resultados dos Testes

### Formato de Saída
```
🚀 Iniciando Teste Completo do Sistema de Tools
======================================================================
✅ VM está rodando e respondendo!

💾 Criando backup da configuração atual...
   ✅ Backup criado com 2 tools

======================================================================
🧪 EXECUTANDO TESTES
======================================================================
🧪 Testando funcionalidade do processador de ferramentas...
   1️⃣ Inicializando processador...
      ✅ Processador inicializado com 2 ferramentas
   ...

======================================================================
🔄 RESTAURANDO CONFIGURAÇÃO ORIGINAL
======================================================================
🔄 Restaurando configuração original...
   ✅ Tool grayscale_filter restaurada
   ✅ Tool blob_1 restaurada
   ✅ Configuração original restaurada

======================================================================
📊 RESULTADOS DOS TESTES
======================================================================
Processador de Ferramentas: ✅ PASSOU
Comando config_tool: ✅ PASSOU
Comando delete_tool: ✅ PASSOU
Tratamento de Erros: ✅ PASSOU

📈 Resumo: 4/4 testes passaram
🎉 Todos os testes passaram com sucesso!
```

### Códigos de Saída
- **0**: Todos os testes passaram
- **1**: Algum teste falhou

## 🛡️ Segurança e Confiabilidade

### **Proteções Implementadas**
1. **Backup Automático**: Configuração salva antes dos testes
2. **Try-Finally**: Restauração garantida mesmo com falhas
3. **Validação de Conexão**: Verifica se VM está ativa
4. **Tratamento de Erros**: Captura e trata todas as exceções
5. **Rollback Completo**: Restaura todas as tools originais

### **Cenários de Falha**
- **VM Offline**: Teste aborta com mensagem clara
- **Erro de Backup**: Teste não inicia
- **Falha nos Testes**: Configuração é restaurada
- **Erro de Restauração**: Logs detalhados para debugging

## 🔧 Configuração de Teste

### **Imagem de Teste**
- **Dimensões**: 640x480 pixels (padrão de câmera)
- **Conteúdo**: Retângulos simulando blobs
- **ROI**: Configurado para testar ferramentas específicas

### **Ferramentas de Teste**
- **Grayscale Filter**: Conversão para escala de cinza
- **Blob Tool**: Detecção de objetos na imagem
- **Math Tool**: Operações matemáticas simples

## 📝 Logs e Debugging

### **Níveis de Log**
- **💾 Backup**: Operações de backup/restauração
- **🧪 Testes**: Execução dos testes individuais
- **🔄 Restauração**: Processo de restauração
- **📊 Resultados**: Resumo final dos testes

### **Informações de Debug**
- **Status da VM**: Verificação de conectividade
- **Configurações**: Detalhes das tools testadas
- **Respostas da API**: Status codes e mensagens
- **Tempos de Processamento**: Performance das ferramentas

## 🚨 Solução de Problemas

### **VM Não Responde**
```bash
# Verificar se VM está rodando
curl http://localhost:5000/api/error

# Verificar logs da VM
tail -f vm.log
```

### **Teste Falha na Restauração**
```bash
# Verificar configuração atual
curl http://localhost:5000/api/inspection_config

# Restaurar manualmente se necessário
python restore_config.py
```

### **Dependências Ausentes**
```bash
# Instalar dependências
pip install requests opencv-python numpy

# Verificar inspection_processor
python -c "import inspection_processor"
```

## 🔄 Integração com CI/CD

### **Execução Automatizada**
```bash
# Script de CI/CD
#!/bin/bash
cd vision_machine
python test_tools.py
exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo "✅ Testes de tools passaram"
    exit 0
else
    echo "❌ Testes de tools falharam"
    exit 1
fi
```

### **Verificações Pré-Teste**
- ✅ VM ativa e respondendo
- ✅ Dependências instaladas
- ✅ Configuração válida
- ✅ Permissões adequadas

## 📚 Arquivos Relacionados

- **`test_tools.py`**: Arquivo principal de testes
- **`vm.py`**: Implementação dos comandos
- **`inspection_processor.py`**: Processador de ferramentas
- **`vm_config.json`**: Configuração da VM

## 🎯 Benefícios do Sistema

1. **Segurança**: Nunca perde configurações de produção
2. **Confiabilidade**: Testes isolados e reproduzíveis
3. **Manutenibilidade**: Um único arquivo para todos os testes
4. **Automação**: Pronto para CI/CD
5. **Debugging**: Logs detalhados para troubleshooting

## 🏁 Conclusão

O sistema de testes de tools implementa uma abordagem robusta e segura para validar todas as funcionalidades relacionadas a ferramentas da Vision Machine. Com backup automático e restauração garantida, os testes podem ser executados com confiança em qualquer ambiente.
