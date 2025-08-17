# Configuração de Trigger da Vision Machine

A Vision Machine suporta dois tipos de configuração de trigger para controlar quando as inspeções são executadas:

## 1. Modo Contínuo (`continuous`)

**Configuração:**
```json
{
  "trigger_config": {
    "type": "continuous",
    "interval_ms": 500
  }
}
```

**Comportamento:**
- Executa inspeções automaticamente a cada intervalo especificado
- O parâmetro `interval_ms` define o intervalo entre inspeções em milissegundos
- Intervalo mínimo: 100ms (para evitar sobrecarga do sistema)
- Ideal para monitoramento contínuo e testes automatizados

**Exemplo de uso:**
```bash
# Configurar para executar a cada 1 segundo
curl -X PUT http://localhost:5000/api/trigger_config \
  -H "Content-Type: application/json" \
  -d '{"type": "continuous", "interval_ms": 1000}'
```

## 2. Modo Gatilho (`trigger`)

**Configuração:**
```json
{
  "trigger_config": {
    "type": "trigger"
  }
}
```

**Comportamento:**
- Executa inspeções apenas quando solicitado explicitamente
- Não usa o parâmetro `interval_ms`
- A VM fica em estado de espera até receber comando de trigger
- Ideal para inspeções sob demanda ou controladas por eventos externos

**Exemplo de uso:**
```bash
# Configurar modo gatilho
curl -X PUT http://localhost:5000/api/trigger_config \
  -H "Content-Type: application/json" \
  -d '{"type": "trigger"}'

# Iniciar inspeção
curl -X POST http://localhost:5000/api/control \
  -H "Content-Type: application/json" \
  -d '{"command": "start_inspection"}'

# Solicitar execução de uma inspeção
curl -X POST http://localhost:5000/api/control \
  -H "Content-Type: application/json" \
  -d '{"command": "trigger"}'
```

## Fluxo de Operação

### Modo Contínuo:
1. Configurar `trigger_config.type = "continuous"`
2. Definir `interval_ms` desejado
3. Iniciar inspeção com `start_inspection`
4. A VM executa automaticamente a cada intervalo

### Modo Gatilho:
1. Configurar `trigger_config.type = "trigger"`
2. Iniciar inspeção com `start_inspection`
3. A VM fica aguardando comandos de trigger
4. Enviar comando `trigger` para executar uma inspeção
5. Repetir passo 4 para cada inspeção desejada

## Verificação de Status

Para verificar o status atual do trigger:

```bash
curl http://localhost:5000/api/status
```

**Resposta inclui:**
```json
{
  "trigger_info": {
    "type": "trigger",
    "interval_ms": 500,
    "waiting_for_trigger": true
  }
}
```

- `type`: Tipo de trigger atual
- `interval_ms`: Intervalo configurado (apenas modo contínuo)
- `waiting_for_trigger`: Se está aguardando trigger (apenas modo gatilho)

## Validações

- O tipo deve ser exatamente `"continuous"` ou `"trigger"`
- No modo contínuo, `interval_ms` deve ser >= 100ms
- Comando `trigger` só é válido quando:
  - `trigger_config.type = "trigger"`
  - Status da VM = `"running"`

## Casos de Uso

### Modo Contínuo:
- Testes automatizados
- Monitoramento contínuo de produção
- Validação de algoritmos
- Coleta de dados para treinamento

### Modo Gatilho:
- Inspeções sob demanda
- Controle por eventos externos
- Integração com sistemas de produção
- Testes manuais ou controlados
