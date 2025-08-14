# Protocolo de Comunicação AnalyticLens

## Visão Geral

Este documento define o protocolo oficial de comunicação entre o **Django Orquestrador** e as **Máquinas de Visão (Flask)** no sistema AnalyticLens, implementando **conexão ponto-a-ponto** com **modos de operação** otimizados.

## Arquitetura de Comunicação

```
┌─────────────────────┐    ┌─────────────────────┐
│   Django Server     │    │   Máquina Flask     │
│   (Orquestrador)    │◄──►│   (Visão Comput.)   │
│                     │    │                     │
│   • Conexão         │    │   • Modo RUN        │
│     Exclusiva       │    │   • Modo TESTE      │
│   • Controle Total  │    │   • Heartbeat       │
│   • Streaming       │    │   • Logs em Memória │
│   • Distribuição    │    │   • Source Config   │
│     de Inspeções    │    │   • Trigger Config  │
└─────────────────────┘    └─────────────────────┘
          │                           │
          │                           │
          ▼                           ▼
┌─────────────────────┐    ┌─────────────────────┐
│   API REST          │    │   API REST          │
│   + Webhooks        │    │   + Heartbeat       │
│   + Streaming       │    │   + Modos de Op.    │
│   + Inspeções       │    │   + Config Local    │
└─────────────────────┘    └─────────────────────┘
```

## **🆕 Nova Estratégia de Comunicação**

### **Conexão Ponto-a-Ponto**
- **Exclusividade**: Apenas um orquestrador pode conectar com uma VM por vez
- **Heartbeat de Ocupação**: VM responde "OCUPADA" para outros orquestradores
- **Controle Total**: Orquestrador conectado tem controle exclusivo da máquina

### **Modos de Operação da VM**

#### **Modo RUN (Execução Contínua)**
- **Comportamento**: Executa inspeções conforme configurado
- **Webhook**: Resultados + imagem em stream a cada 2 segundos
- **Performance**: Máxima velocidade de processamento
- **Uso**: Produção e monitoramento contínuo
- **🆕 Configuração**: Source e trigger configurados localmente na VM

#### **Modo TESTE (Processamento Controlado)**
- **Comportamento**: Processa inspeções com delay controlado
- **Resposta**: Máximo de 2 segundos entre respostas
- **Performance**: Controlada para análise detalhada
- **Uso**: Desenvolvimento, teste e validação
- **🆕 Configuração**: Source e trigger configurados localmente na VM

### **Sistema de Logs e Streaming**
- **Logs em Memória**: Resultados e imagens armazenados localmente
- **Streaming Independente**: Download de logs sem interferir na inspeção
- **Configurável**: Período de retenção e formato dos logs

### **🆕 Configuração Local da VM**
- **Source de Imagens**: Configurado diretamente na VM (câmera, arquivo, stream)
- **Tipo de Trigger**: Configurado diretamente na VM (contínuo, por evento, manual)
- **Parâmetros de Captura**: Resolução, FPS, formato configurados na VM
- **Orquestrador**: Apenas envia inspeções e recebe resultados

## Estrutura do Protocolo

### 1. **Autenticação e Segurança**
- [Autenticação Mútua](./01-Autenticacao/README.md)
- [IP Whitelist](./01-Autenticacao/IP-Whitelist.md)
- [Tokens de Sessão](./01-Autenticacao/Tokens.md)
- [Conexão Exclusiva](./01-Autenticacao/Conexao-Exclusiva.md)

### 2. **APIs REST**
- [API Django (Orquestrador)](./02-APIs/API-Django.md)
- [API Flask (Máquinas)](./02-APIs/API-Flask.md)
- [Endpoints Comuns](./02-APIs/Endpoints.md)
- [Modos de Operação](./02-APIs/Modos-Operacao.md)
- [🆕 Configuração Local](./02-APIs/Configuracao-Local.md)

### 3. **Webhooks e Comunicação Assíncrona**
- [Contratos de Webhook](./03-Webhooks/README.md)
- [Heartbeat](./03-Webhooks/Heartbeat.md)
- [Resultados de Inspeção](./03-Webhooks/Resultados.md)
- [Streaming de Imagens](./03-Webhooks/Streaming-Imagens.md)

### 4. **Formatos de Dados**
- [Schemas JSON](./04-Formato-Dados/README.md)
- [Validações](./04-Formato-Dados/Validacoes.md)
- [Tipos de Dados](./04-Formato-Dados/Tipos.md)
- [Estrutura de Logs](./04-Formato-Dados/Estrutura-Logs.md)
- [🆕 Configurações de Source](./04-Formato-Dados/Source-Config.md)

### 5. **Tratamento de Erros**
- [Códigos de Erro](./05-Tratamento-Erros/README.md)
- [Estratégias de Retry](./05-Tratamento-Erros/Retry.md)
- [Logs e Auditoria](./05-Tratamento-Erros/Logs.md)
- [Conflitos de Conexão](./05-Tratamento-Erros/Conflitos-Conexao.md)

### 6. **Fluxos de Trabalho**
- [Handshake Inicial](./06-Fluxos/Handshake.md)
- [Distribuição de Inspeções](./06-Fluxos/Distribuicao.md)
- [Coleta de Resultados](./06-Fluxos/Coleta.md)
- [Controle de Modos](./06-Fluxos/Controle-Modos.md)
- [Streaming de Logs](./06-Fluxos/Streaming-Logs.md)
- [🆕 Configuração de Source](./06-Fluxos/Configuracao-Source.md)

### 7. **Exemplos e Casos de Uso**
- [Exemplos de Implementação](./07-Exemplos/README.md)
- [Casos de Teste](./07-Exemplos/Casos-Teste.md)
- [Troubleshooting](./07-Exemplos/Troubleshooting.md)
- [Configuração de Modos](./07-Exemplos/Configuracao-Modos.md)
- [🆕 Configuração de Source](./07-Exemplos/Configuracao-Source.md)

## Versão do Protocolo

**Versão Atual**: 2.1.0  
**Data**: Agosto 2025  
**Status**: Em Desenvolvimento  
**Mudanças**: Nova estratégia de conexão ponto-a-ponto, modos de operação e configuração local da VM

## Princípios do Protocolo

1. **Simplicidade**: APIs RESTful simples e intuitivas
2. **Segurança**: Autenticação mútua e validação rigorosa
3. **Confiabilidade**: Tratamento robusto de erros e retry
4. **Escalabilidade**: Suporte a múltiplas máquinas de visão
5. **Monitoramento**: Heartbeat e status em tempo real
6. **Versionamento**: Compatibilidade com versões anteriores
7. **🆕 Exclusividade**: Conexão ponto-a-ponto por máquina
8. **🆕 Modos de Operação**: RUN e TESTE com controle de timing
9. **🆕 Streaming Otimizado**: Logs e imagens sem interferência
10. **🆕 Configuração Local**: Source e trigger configurados na VM

## Implementação

### Django (Orquestrador)
- Implementa endpoints REST para gerenciamento
- Recebe webhooks das máquinas de visão
- Gerencia autenticação e autorização
- Distribui inspeções para máquinas disponíveis
- **🆕 Controla modo de operação das VMs**
- **🆕 Gerencia conexão exclusiva por máquina**
- **🆕 Recebe streaming de logs e imagens**
- **🆕 Envia apenas configurações de inspeção (não source/trigger)**

### Flask (Máquinas de Visão)
- Implementa endpoints REST para receber tarefas
- Envia webhooks com resultados e status
- Mantém heartbeat periódico
- Valida autenticação em todas as requisições
- **🆕 Opera em modo RUN ou TESTE**
- **🆕 Mantém logs em memória**
- **🆕 Fornece streaming de dados**
- **🆕 Responde "OCUPADA" para outros orquestradores**
- **🆕 Gerencia configuração local de source e trigger**
- **🆕 Controla parâmetros de captura (resolução, FPS, formato)**

## **🆕 Fluxo de Configuração Simplificado**

### **1. Configuração da VM (Local)**
```
VM Flask:
├── Source de Imagens
│   ├── Câmera USB (resolução, FPS)
│   ├── Arquivo de vídeo
│   ├── Stream RTSP/HTTP
│   └── Diretório de imagens
├── Tipo de Trigger
│   ├── Contínuo (a cada X ms)
│   ├── Por evento (motion detection)
│   ├── Manual (comando)
│   └── Agendado (cron)
└── Parâmetros de Captura
    ├── Resolução
    ├── FPS
    ├── Formato
    └── Qualidade
```

### **2. Orquestrador (Apenas Inspeções)**
```
Django Orquestrador:
├── Envia configuração de inspeção
│   ├── Algoritmo de análise
│   ├── Parâmetros de threshold
│   ├── Regras de classificação
│   └── Ações de resultado
├── Recebe resultados
├── Controla modo de operação
└── Gerencia conexão exclusiva
```

## Contribuição

Este protocolo é um documento vivo e deve ser atualizado conforme a implementação evolui. Todas as mudanças devem ser documentadas e versionadas adequadamente.

## Contato

Para dúvidas sobre o protocolo, consulte a documentação específica de cada seção ou entre em contato com a equipe de desenvolvimento.
