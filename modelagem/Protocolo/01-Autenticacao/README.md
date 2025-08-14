# Autenticação e Segurança

## Visão Geral

O sistema de autenticação do AnalyticLens é baseado em **autenticação mútua** entre o Django Orquestrador e as Máquinas de Visão Flask, garantindo que apenas sistemas autorizados possam se comunicar.

## Arquitetura de Segurança

```
┌─────────────────────┐    ┌─────────────────────┐
│   Django Server     │◄──►│   Máquina Flask     │
│   (Orquestrador)    │    │   (Visão Comput.)   │
│                     │    │                     │
│   • IP Whitelist    │    │   • IP Whitelist    │
│   • Token Público   │    │   • Token Público   │
│   • Token Sessão    │    │   • Token Sessão    │
└─────────────────────┘    └─────────────────────┘
```

## Camadas de Segurança

### 1. **IP Whitelist (Primeira Camada)**
- Cada máquina Flask mantém uma lista de IPs autorizados
- Apenas conexões vindas de IPs na whitelist são aceitas
- Configuração manual pelo usuário no Django

### 2. **Token Público (Segunda Camada)**
- Identificador único para cada máquina de visão
- Gerado automaticamente pelo Django durante o cadastro
- Usado para validação inicial e handshake

### 3. **Token de Sessão (Terceira Camada)**
- Token temporário para comunicação contínua
- Gerado após validação bem-sucedida do IP + Token Público
- Expira após tempo definido (padrão: 24 horas)

## Fluxo de Autenticação

### **Fase 1: Cadastro da Máquina**
```
1. Usuário cadastra máquina no Django
2. Django gera Token Público único
3. Usuário configura IP Whitelist na máquina
4. Máquina armazena Token Público + IP Whitelist
```

### **Fase 2: Handshake Inicial**
```
1. Django tenta conectar com a máquina
2. Máquina valida IP do Django
3. Django envia Token Público
4. Máquina valida Token Público
5. Máquina gera Token de Sessão
6. Ambos estabelecem confiança mútua
```

### **Fase 3: Comunicação Contínua**
```
1. Django usa Token de Sessão para todas as operações
2. Máquina valida Token + IP em cada requisição
3. Sessão expira após tempo definido
4. Renovação automática ou novo handshake
```

## Implementação

### **Django (Orquestrador)**
```python
# Exemplo de configuração de segurança
SECURITY_CONFIG = {
    'ip_whitelist': ['192.168.1.100', '10.0.0.50'],
    'public_token': 'mv_abc123def456',
    'session_token_expiry': 86400,  # 24 horas
    'max_retry_attempts': 3
}
```

### **Flask (Máquina de Visão)**
```python
# Exemplo de configuração de segurança
SECURITY_CONFIG = {
    'ip_whitelist': ['192.168.1.10'],  # IP do Django
    'public_token': 'mv_abc123def456',
    'session_token': None,  # Gerado durante handshake
    'session_expiry': None
}
```

## Validações de Segurança

### **Em Cada Requisição:**
1. **Validação de IP**: Verificar se origem está na whitelist
2. **Validação de Token**: Verificar se token de sessão é válido
3. **Validação de Expiração**: Verificar se sessão não expirou
4. **Validação de Formato**: Verificar estrutura da requisição

### **Logs de Segurança:**
- Todas as tentativas de conexão (sucesso/falha)
- IPs de origem de cada requisição
- Tokens utilizados (hash para segurança)
- Timestamps de todas as operações

## Tratamento de Falhas

### **Falha de IP Whitelist:**
- Rejeitar conexão imediatamente
- Log de tentativa de acesso não autorizado
- Alertar administrador se configurado

### **Falha de Token Público:**
- Rejeitar handshake
- Log de tentativa de autenticação inválida
- Sugerir verificação de configuração

### **Falha de Token de Sessão:**
- Rejeitar operação
- Solicitar novo handshake
- Log de sessão expirada

### **Falha de Rede:**
- Implementar retry com backoff exponencial
- Log de tentativas de reconexão
- Fallback para modo offline se configurado

## Configuração de Segurança

### **Parâmetros Recomendados:**
- **IP Whitelist**: Apenas IPs da rede corporativa
- **Token Público**: 32+ caracteres aleatórios
- **Expiração de Sessão**: 24 horas (configurável)
- **Tentativas de Retry**: 3 com backoff exponencial
- **Logs de Segurança**: Manter por 90 dias

### **Monitoramento:**
- Alertas para tentativas de acesso não autorizado
- Dashboard de status de segurança
- Relatórios de auditoria mensais
- Notificações para administradores

## Próximos Passos

1. [IP Whitelist](./IP-Whitelist.md) - Detalhes da implementação
2. [Tokens](./Tokens.md) - Geração e validação de tokens
3. [Implementação](./Implementacao.md) - Código de exemplo
4. [Testes](./Testes.md) - Casos de teste de segurança
