# Componente VMsTable

## Descrição
O componente `VMsTable` é uma tabela responsiva e interativa para exibir e gerenciar máquinas virtuais (VMs) do sistema AnalyticLens. Ele utiliza Bootstrap Vue 3 para fornecer uma interface moderna e funcional.

## Funcionalidades

### 📊 **Exibição de Dados**
- Lista todas as VMs com informações relevantes
- Campos exibidos: ID, Nome, Status, Conexão, Modo, Fonte, Resolução, FPS, Última Atividade
- Paginação automática com configuração de itens por página

### 🔍 **Busca e Filtros**
- Campo de busca por nome, ID ou descrição
- Filtros por status da VM (Executando, Parada, Erro, etc.)
- Filtros por status de conexão (Conectado, Desconectado, etc.)
- Busca em tempo real com debounce

### 🎯 **Gerenciamento de Status**
- Badges coloridos para diferentes status:
  - **Status**: Executando (verde), Parada (amarelo), Erro (vermelho), Manutenção (azul), Offline (cinza)
  - **Conexão**: Conectado (verde), Desconectado (amarelo), Conectando (azul), Erro (vermelho)
  - **Modo**: Produção (vermelho), Teste (amarelo), Desenvolvimento (azul)

### ⚡ **Ações em Tempo Real**
- Botões de ação condicionais baseados no estado da VM:
  - ▶️ **Iniciar** (quando `can_start = true`)
  - ⏸️ **Parar** (quando `can_stop = true`)
  - 🔄 **Reiniciar** (quando `can_restart = true`)
  - 👁️ **Ver Detalhes** (sempre disponível)

### 📈 **Resumo de Status**
- Cards informativos com contadores:
  - Total de VMs
  - VMs Executando
  - VMs Paradas
  - VMs com Erro

### 🔄 **Atualização Automática**
- Atualização automática do resumo de status a cada 30 segundos (configurável)
- Botão manual de atualização
- Indicador de carregamento durante operações

## Uso

### Importação
```vue
import VMsTable from '@/components/VMsTable.vue'
```

### Template Básico
```vue
<template>
  <VMsTable
    ref="vmsTableRef"
    :refresh-interval="30000"
    @vm-action="handleVMAction"
    @refresh="handleRefresh"
    @error="handleError"
  />
</template>
```

### Props
| Prop | Tipo | Padrão | Descrição |
|------|------|--------|-----------|
| `refresh-interval` | Number | 30000 | Intervalo de atualização automática em ms (0 = desabilitado) |

### Events
| Event | Payload | Descrição |
|-------|---------|-----------|
| `vm-action` | `{action, vmId, success, error?}` | Emitido quando uma ação é executada na VM |
| `refresh` | - | Emitido quando os dados são atualizados |
| `error` | `string` | Emitido quando ocorre um erro |

### Métodos Expostos
| Método | Descrição |
|--------|-----------|
| `refresh()` | Força atualização dos dados |
| `fetchVMs()` | Busca lista de VMs da API |
| `fetchStatusSummary()` | Busca resumo de status da API |

## API Endpoints Utilizados

### GET `/api/vms`
- **Parâmetros**: `page`, `per_page`, `search`, `status`, `connection_status`
- **Retorna**: Lista paginada de VMs com metadados de paginação

### GET `/api/vms/status/summary`
- **Retorna**: Resumo estatístico de todas as VMs

### POST `/api/vms/{id}/action`
- **Body**: `{action: 'start'|'stop'|'restart'}`
- **Retorna**: Confirmação da ação executada

## Estrutura de Dados

### VM Object
```typescript
interface VM {
  id: number
  machine_id: string
  name: string
  description: string
  status: 'running' | 'stopped' | 'error' | 'maintenance' | 'offline'
  mode: 'PRODUCAO' | 'TESTE' | 'DESENVOLVIMENTO'
  connection_status: 'connected' | 'disconnected' | 'connecting' | 'error'
  source_type: string
  resolution: string
  fps: number
  last_heartbeat: string
  can_start: boolean
  can_stop: boolean
  can_restart: boolean
}
```

### Pagination Object
```typescript
interface Pagination {
  page: number
  per_page: number
  total_pages: number
  total_count: number
  has_next: boolean
  has_previous: boolean
}
```

## Estilização

### Classes CSS Principais
- `.vms-table` - Container principal
- `.table-header` - Cabeçalho com filtros
- `.vms-table-main` - Tabela principal
- `.status-badge` - Badges de status
- `.status-summary` - Resumo de status
- `.status-card` - Cards individuais do resumo

### Responsividade
- Layout adaptativo para dispositivos móveis
- Filtros empilhados em telas pequenas
- Botões de ação responsivos
- Tabela com scroll horizontal quando necessário

## Dependências

### Externas
- **Bootstrap Vue 3**: Componentes de UI
- **Vue Router**: Navegação para detalhes da VM

### Internas
- **Icon.vue**: Componente de ícones
- **http.js**: Utilitário para requisições HTTP

## Exemplo de Implementação Completa

```vue
<template>
  <div>
    <h1>Gerenciamento de VMs</h1>
    
    <VMsTable
      ref="vmsTableRef"
      :refresh-interval="60000"
      @vm-action="handleVMAction"
      @refresh="handleRefresh"
      @error="handleError"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import VMsTable from '@/components/VMsTable.vue'

const vmsTableRef = ref(null)

const handleVMAction = (actionData) => {
  if (actionData.success) {
    console.log(`VM ${actionData.action} executada com sucesso`)
  } else {
    console.error(`Erro: ${actionData.error}`)
  }
}

const handleRefresh = () => {
  console.log('Dados atualizados')
}

const handleError = (error) => {
  console.error('Erro na tabela:', error)
}
</script>
```

## Notas de Desenvolvimento

- O componente utiliza Composition API com `<script setup>`
- Todas as operações assíncronas incluem tratamento de erro
- Os dados são atualizados automaticamente para manter sincronização
- O componente é totalmente responsivo e acessível
- Suporte completo a internacionalização (português brasileiro)
