# Teste de Trigger Controlado pelo Usuário

## 🎮 **Novos Comandos de Trigger Adicionados**

O `test_user_vm.py` agora inclui comandos específicos para testar e controlar os dois tipos de trigger da Vision Machine.

## 📋 **Comandos de Trigger Disponíveis:**

### **1. `trigger_continuous <ms>`**
Configura o trigger para modo contínuo com intervalo especificado.

**Uso:**
```bash
trigger_continuous 1000    # 1 segundo
trigger_continuous 500     # 500ms
trigger_continuous 2000    # 2 segundos
```

**Comportamento:**
- A VM executa inspeções automaticamente a cada intervalo
- Ideal para monitoramento contínuo
- Não requer comandos manuais para executar

### **2. `trigger_trigger`**
Configura o trigger para modo gatilho.

**Uso:**
```bash
trigger_trigger
```

**Comportamento:**
- A VM fica aguardando comandos de trigger
- Executa inspeções apenas quando solicitado
- Ideal para controle manual ou eventos externos



### **3. `send_trigger`**
Envia um trigger manual (apenas válido em modo gatilho).

**Uso:**
```bash
send_trigger
```

**Comportamento:**
- Executa uma inspeção imediatamente
- Só funciona quando `trigger_config.type = "trigger"`
- Requer que inspeção esteja rodando

## 🔄 **Fluxo de Teste Recomendado:**

### **Teste Rápido:**
```bash
# 1. Verificar status atual
status

# 2. Configurar trigger desejado
trigger_continuous 1000    # ou trigger_trigger

# 3. Iniciar inspeção
start

# 4. Verificar resultados
results
```

### **Teste Manual Passo a Passo:**

#### **Modo Contínuo:**
```bash
# 1. Configurar trigger contínuo
trigger_continuous 1000

# 2. Iniciar inspeção
start

# 3. Aguardar processamento automático
# (aguardar alguns segundos)

# 4. Parar inspeção
stop

# 5. Verificar resultados
results
```

#### **Modo Gatilho:**
```bash
# 1. Configurar trigger gatilho
trigger_trigger

# 2. Iniciar inspeção
start

# 3. Enviar triggers manuais
send_trigger
send_trigger
send_trigger

# 4. Parar inspeção
stop

# 5. Verificar resultados
results
```

## 📊 **Comandos de Verificação:**

### **Status Geral:**
```bash
status          # Status completo da VM
```

### **Configuração de Trigger:**
```bash
trigger         # Configuração atual do trigger
```

### **Resultados:**
```bash
results         # Resultados recebidos via WebSocket
clear           # Limpa resultados
```

## 🧪 **Cenários de Teste:**

### **Cenário 1: Validação de Modo Contínuo**
```bash
trigger_continuous 500
start
# Aguardar 10 segundos
stop
results
```

### **Cenário 2: Validação de Modo Gatilho**
```bash
trigger_trigger
start
send_trigger
send_trigger
send_trigger
stop
results
```



## ⚠️ **Validações Importantes:**

### **Modo Contínuo:**
- ✅ Executa automaticamente a cada intervalo
- ❌ Comando `send_trigger` é rejeitado
- ✅ Ideal para testes automatizados

### **Modo Gatilho:**
- ✅ Aguarda comandos de trigger
- ✅ Comando `send_trigger` é aceito
- ❌ Não executa automaticamente
- ✅ Ideal para controle manual

## 🔧 **Configurações Recomendadas:**

### **Para Desenvolvimento:**
```bash
trigger_continuous 500    # 500ms - rápido para testes
```

### **Para Produção:**
```bash
trigger_continuous 1000   # 1s - balanceado
trigger_continuous 2000   # 2s - conservador
```

### **Para Controle Manual:**
```bash
trigger_trigger          # Aguarda comandos
```

## 📝 **Dicas de Uso:**

1. **Sempre verifique o status** antes de mudar configurações
2. **Configure o trigger desejado** antes de iniciar inspeção
3. **Monitore resultados** com `results` após cada teste
4. **Conecte WebSocket** para receber dados em tempo real
5. **Teste ambos os modos** manualmente para validação completa

## 🎯 **Resultado Esperado:**

Com esses comandos, você pode:
- ✅ **Configurar** qualquer tipo de trigger
- ✅ **Controlar** manualmente o processamento
- ✅ **Validar** o comportamento esperado
- ✅ **Monitorar** resultados em tempo real
- ✅ **Ter controle total** sobre cada etapa do teste

Os comandos manuais permitem controle granular e testes personalizados! 🎉
