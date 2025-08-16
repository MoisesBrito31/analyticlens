# AnalyticLens - Vision Machine (VM)

## 📋 Visão Geral

A **Vision Machine (VM)** é um servidor Flask robusto e inteligente para máquinas de visão computacional. O sistema implementa uma arquitetura modular com persistência automática, tratamento robusto de erros, e comunicação em tempo real via WebSocket.

## 🚀 Funcionalidades Principais

### ✨ **Sistema Robusto e Auto-Recuperável**
- **Persistência automática**: Configurações salvas automaticamente em `vm_config.json`
- **Auto-start inteligente**: Inicia inspeção automaticamente quando possível
- **Recriação automática**: Recria `ImageSource` quando necessário
- **Tratamento de erros**: Sistema robusto de recuperação sem quebrar a aplicação

### 🎯 **Gerenciamento de Imagens Inteligente**
- **3 tipos de source**: `pasta`, `camera`, `camera_IP` (RTSP)
- **Fila cíclica**: Processamento contínuo de imagens de pasta
- **Fallback automático**: Tenta recriar source em caso de erro
- **Validação robusta**: Verifica disponibilidade antes de processar

### 🔄 **Modos de Operação**
- **TESTE**: Modo de desenvolvimento com processamento simulado
- **RUN**: Modo de produção (preparado para implementação real)
- **Transição automática**: Entre modos com validação

### 📡 **Comunicação em Tempo Real**
- **WebSocket SocketIO**: Comunicação bidirecional
- **Rate limiting**: 1 atualização por segundo para modo teste
- **Eventos estruturados**: `test_result`, `status_update`, `connected`

## 🏗️ Arquitetura do Sistema

### **Classes Principais**

#### **VisionMachine** - Cérebro do Sistema
```python
class VisionMachine:
    # Gerencia estado, configurações e componentes
    - Estado: idle, running, error
    - Persistência automática em JSON
    - Auto-start de inspeção
    - Gerenciamento de erros
```

#### **ImageSource** - Gerenciador de Fontes
```python
class ImageSource:
    # Gerencia diferentes tipos de entrada de imagem
    - pasta: Fila cíclica de arquivos
    - camera: Câmera local via OpenCV
    - camera_IP: Stream RTSP
    - Recriação automática em caso de erro
```

#### **TestModeProcessor** - Processador de Teste
```python
class TestModeProcessor:
    # Processa frames em modo teste
    - Thread assíncrono de processamento
    - Simulação de inspeção
    - WebSocket com rate limiting
    - Tratamento robusto de erros
```

#### **FlaskVisionServer** - Servidor Web
```python
class FlaskVisionServer:
    # Servidor Flask principal
    - API REST completa
    - WebSocket SocketIO
    - Handlers de shutdown graceful
    - Auto-start de inspeção
```

## 🔧 Configuração e Uso

### **Instalação de Dependências**
```bash
pip install -r requirements.txt
```

### **Execução Básica**
```bash
python vm.py
```

### **Execução com Parâmetros**
```bash
python vm.py --machine-id vm_001 --port 5000 --debug
```

### **Parâmetros Disponíveis**
- `--machine-id`: ID único da máquina (padrão: vm_001)
- `--django-url`: URL do Django orquestrador (padrão: http://localhost:8000)
- `--config-file`: Arquivo de configuração personalizado
- `--host`: Host para bind do servidor (padrão: 0.0.0.0)
- `--port`: Porta do servidor (padrão: 5000)
- `--debug`: Modo debug

## 📡 API REST

### **Endpoints Principais**

#### **GET /api/status**
Retorna o status atual da VM:
```json
{
  "machine_id": "vm_001",
  "status": "idle",
  "mode": "TESTE",
  "connection_status": "disconnected",
  "error_msg": "",
  "timestamp": "2025-08-16T04:00:00.000000",
  "source_config": {...},
  "trigger_config": {...},
  "source_available": true
}
```

#### **POST /api/control**
Controla a VM com comandos:
```json
{
  "command": "start_inspection"
}
```

**Comandos disponíveis:**
- `change_mode`: Altera modo (TESTE/RUN)
- `start_inspection`: Inicia inspeção
- `stop_inspection`: Para inspeção
- `update_inspection_config`: Atualiza configuração

#### **PUT /api/source_config**
Configura fonte de imagem:
```json
{
  "type": "pasta",
  "folder_path": "./test_images"
}
```

**Tipos de source:**
- `pasta`: Pasta com imagens (fila cíclica)
- `camera`: Câmera local por ID
- `camera_IP`: Stream RTSP

#### **GET/PUT /api/trigger_config**
Gerencia configuração de trigger:
```json
{
  "type": "continuous",
  "interval_ms": 1000
}
```

#### **GET/POST/DELETE /api/error**
Gerencia mensagens de erro:
- `GET`: Obtém informações de erro
- `POST`: Define mensagem de erro
- `DELETE`: Limpa erro

## 🔌 WebSocket (SocketIO)

### **Eventos Disponíveis**

#### **Eventos de Cliente → Servidor**
- `connect`: Conecta ao servidor
- `disconnect`: Desconecta do servidor
- `request_status`: Solicita status atual

#### **Eventos de Servidor → Cliente**
- `connected`: Confirma conexão
- `status_update`: Atualização de status
- `test_result`: Resultado de processamento de teste

### **Exemplo de Resultado de Teste**
```json
{
  "aprovados": 5,
  "reprovados": 1,
  "frame": 6,
  "time": "23ms",
  "tools": {},
  "timestamp": "2025-08-16T04:00:00.000000",
  "source_type": "pasta",
  "mode": "TESTE"
}
```

## ⚙️ Configuração

### **Arquivo de Configuração (vm_config.json)**
```json
{
  "machine_id": "vm_001",
  "django_url": "http://localhost:8000",
  "status": "idle",
  "mode": "TESTE",
  "connection_status": "disconnected",
  "inspection_config": {},
  "source_config": {
    "type": "pasta",
    "folder_path": "./test_images",
    "camera_id": 0,
    "resolution": [640, 480],
    "fps": 30,
    "rtsp_url": ""
  },
  "trigger_config": {
    "type": "continuous",
    "interval_ms": 1000
  },
  "error_msg": "",
  "last_saved": "2025-08-16T04:00:00.000000"
}
```

### **Configurações Padrão**
- **Status inicial**: `idle`
- **Modo inicial**: `TESTE`
- **Source padrão**: `pasta` com `./test_images`
- **Trigger**: `continuous` com 1000ms
- **Resolução**: 640x480 @ 30fps

## 🧪 Testes

### **Script de Teste Automatizado**
```bash
python test_vm.py
```

**Testes incluídos:**
- ✅ Endpoints da API
- ✅ Configuração de source
- ✅ Controle de modo
- ✅ Controle de inspeção
- ✅ WebSocket básico
- ✅ WebSocket com processamento
- ✅ Sistema de tratamento de erros
- ✅ Limpeza e restauração

### **Script de Teste Interativo**
```bash
python test_user_vm.py
```

**Comandos disponíveis:**
- `status`: Mostra status atual
- `mode <TESTE/RUN>`: Altera modo
- `start`: Inicia inspeção
- `stop`: Para inspeção
- `source_pasta <path>`: Configura source para pasta
- `source_camera <id>`: Configura source para câmera
- `source_rtsp <url>`: Configura source para RTSP
- `error`: Mostra informações de erro
- `set_error <msg>`: Define mensagem de erro
- `clear_error`: Limpa erro

## 🛡️ Tratamento de Erros

### **Sistema de Recuperação Automática**
1. **Detecção**: Identifica quando `ImageSource` está quebrado
2. **Recriação**: Tenta recriar automaticamente
3. **Fallback**: Se falhar, define status de erro
4. **Recuperação**: Permite recriar manualmente via API

### **Estados de Erro**
- **`idle`**: Estado normal, pronto para operação
- **`running`**: Processando inspeção
- **`error`**: Erro ativo, inspeção parada

### **Comportamento em Caso de Erro**
- ✅ **Não quebra**: Aplicação continua funcionando
- ✅ **API disponível**: Endpoints continuam respondendo
- ✅ **Recuperação**: Pode ser resolvido via API
- ✅ **Logs detalhados**: Informações completas para debug

## 🔄 Persistência Automática

### **Fluxo de Configuração**
1. **Inicialização**: Carrega de `vm_config.json` se existir
2. **Padrões**: Usa configurações padrão se arquivo não existir
3. **Salvamento**: Salva automaticamente em todas as mudanças
4. **Recuperação**: Carrega estado salvo na próxima inicialização

### **Auto-Start de Inspeção**
- **Verificação**: Checa se deve iniciar automaticamente
- **Pré-requisitos**: Valida source e modo antes de iniciar
- **Recriação**: Tenta recriar source se necessário
- **Fallback**: Volta para `idle` se não puder iniciar

## 📁 Estrutura de Arquivos

```
vision_machine/
├── vm.py                          # Servidor principal
├── vm_config.json                 # Configuração persistente
├── vm_example_config.json         # Exemplo de configuração
├── test_vm.py                     # Testes automatizados
├── test_user_vm.py                # Teste interativo
├── requirements.txt                # Dependências Python
├── README.md                      # Esta documentação
├── diagrama_classes_vm.puml       # Diagrama de classes
├── source_config_examples.md      # Exemplos de configuração
└── test_images/                   # Pasta de imagens de teste
    ├── image1.bmp
    ├── image2.bmp
    └── ...
```

## 🚀 Casos de Uso

### **Desenvolvimento e Teste**
1. **Configurar source para pasta** com imagens de teste
2. **Executar modo TESTE** para validação
3. **Monitorar via WebSocket** em tempo real
4. **Testar APIs** para validação de funcionalidades

### **Produção**
1. **Configurar source real** (câmera ou RTSP)
2. **Alterar para modo RUN** quando implementar lógica real
3. **Configurar trigger** conforme necessidade
4. **Monitorar via API** de status

### **Integração com Orquestrador**
1. **Configurar django_url** para comunicação
2. **Implementar webhooks** para notificações
3. **Sincronizar status** via API REST
4. **Monitorar conexão** via WebSocket

## 🔧 Troubleshooting

### **Problemas Comuns**

#### **Source de Imagem Não Disponível**
- **Sintoma**: Erro 400 ao iniciar inspeção
- **Solução**: Verificar se pasta existe e tem imagens
- **Prevenção**: Sistema tenta recriar automaticamente

#### **WebSocket Não Conecta**
- **Sintoma**: Timeout na conexão
- **Solução**: Verificar se servidor está rodando na porta correta
- **Prevenção**: Usar `namespaces=['/']` no cliente

#### **Inspeção Não Inicia**
- **Sintoma**: Status permanece `idle`
- **Solução**: Verificar se source está configurado corretamente
- **Prevenção**: Sistema valida source antes de iniciar

### **Logs e Debug**
- **Nível**: INFO por padrão
- **Formato**: Timestamp + Nome + Nível + Mensagem
- **Arquivo**: Console (configurável)
- **Emojis**: Usados para facilitar leitura

## 📈 Roadmap

### **Funcionalidades Futuras**
- [ ] **Lógica real de inspeção**: Substituir simulação
- [ ] **Múltiplas câmeras**: Suporte a arrays de câmeras
- [ ] **Calibração automática**: Sistema de calibração
- [ ] **Machine Learning**: Integração com modelos ML
- [ ] **Dashboard web**: Interface gráfica para monitoramento
- [ ] **Métricas avançadas**: Estatísticas de performance
- [ ] **Backup automático**: Sistema de backup de configurações
- [ ] **Health checks**: Verificações de saúde do sistema

## 🤝 Contribuição

### **Padrões de Código**
- **Python 3.8+**: Compatibilidade com versões modernas
- **Type hints**: Uso de tipos para melhor documentação
- **Docstrings**: Documentação inline de métodos
- **Logging estruturado**: Logs informativos e organizados
- **Tratamento de erros**: Try-catch robusto em operações críticas

### **Estrutura de Commits**
- **feat**: Nova funcionalidade
- **fix**: Correção de bug
- **docs**: Documentação
- **test**: Testes
- **refactor**: Refatoração de código
- **style**: Formatação de código

## 📄 Licença

Este projeto faz parte do sistema **AnalyticLens** e está sob os termos da licença do projeto principal.

## 📞 Suporte

Para dúvidas, sugestões ou problemas:
1. **Verificar logs** para informações detalhadas
2. **Executar testes** para validar funcionalidades
3. **Consultar documentação** para casos de uso
4. **Abrir issue** no repositório do projeto

---

**AnalyticLens Vision Machine** - Sistema robusto e inteligente para visão computacional 🚀
