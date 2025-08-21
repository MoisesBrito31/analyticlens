<template>
  <div class="vms-table">
    <!-- Header com busca e filtros -->
    <div class="table-header mb-3">
      <BRow>
        <BCol cols="12" md="4">
          <BFormInput
            v-model="searchQuery"
            placeholder="Buscar VMs..."
            @keyup.enter="handleSearch"
            class="mb-2"
          />
        </BCol>
        <BCol cols="12" md="3">
          <BFormSelect
            v-model="statusFilter"
            :options="statusOptions"
            @change="handleFilterChange"
            class="mb-2"
          />
        </BCol>
        <BCol cols="12" md="3">
          <BFormSelect
            v-model="connectionFilter"
            :options="connectionOptions"
            @change="handleFilterChange"
            class="mb-2"
          />
        </BCol>
        <BCol cols="12" md="2">
          <BButton
            variant="primary"
            @click="handleSearch"
            :disabled="loading"
            class="w-100"
          >
            <Icon name="search" size="1rem" class="me-1" />
            Buscar
          </BButton>
        </BCol>
      </BRow>
    </div>

    <!-- Resumo de status (movido para cima da tabela) -->
    <div class="status-summary mb-3">
      <div class="status-row">
        <div class="status-col">
          <div class="status-card text-center p-2">
            <div class="status-number text-primary">{{ totalCount }}</div>
            <div class="status-label">Total de VMs</div>
          </div>
        </div>
        <div class="status-col">
          <div class="status-card text-center p-2">
            <div class="status-number text-success">{{ summary.running }}</div>
            <div class="status-label">Rodando</div>
          </div>
        </div>
        <div class="status-col">
          <div class="status-card text-center p-2">
            <div class="status-number text-warning">{{ summary.stopped }}</div>
            <div class="status-label">Paradas</div>
          </div>
        </div>
        <div class="status-col">
          <div class="status-card text-center p-2">
            <div class="status-number text-danger">{{ summary.error }}</div>
            <div class="status-label">Com Erro</div>
          </div>
        </div>
        <div class="status-col">
          <div class="status-card text-center p-2">
            <div class="status-number text-secondary">{{ summary.offline }}</div>
            <div class="status-label">Offline</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Tabela de VMs -->
    <div class="table-container">
      <BTable
        :items="vms"
        :fields="tableFields"
        :busy="loading"
        striped
        hover
        responsive
        class="shadow-sm"
        empty-text="Nenhuma VM encontrada"
        empty-filtered-text="Nenhuma VM corresponde aos filtros aplicados"
      >
        <!-- Status -->
        <template #cell(status)="{ item }">
          <BBadge :variant="getStatusVariant(item.status)">
            {{ getStatusLabel(item.status) }}
          </BBadge>
        </template>

        <!-- Connection Status -->
        <template #cell(connection_status)="{ item }">
          <BBadge :variant="getConnectionVariant(item.connection_status)">
            {{ getConnectionLabel(item.connection_status) }}
          </BBadge>
        </template>

        <!-- Mode -->
        <template #cell(mode)="{ item }">
          <BBadge :variant="getModeVariant(item.mode)">
            {{ getModeLabel(item.mode) }}
          </BBadge>
        </template>

        <!-- Resolution -->
        <template #cell(resolution)="{ item }">
          <span class="text-monospace">{{ item.resolution }}</span>
        </template>

        <!-- Last Heartbeat -->
        <template #cell(last_heartbeat)="{ item }">
          <span v-if="item.last_heartbeat" :title="formatDateTime(item.last_heartbeat)">
            {{ formatRelativeTime(item.last_heartbeat) }}
          </span>
          <span v-else class="text-muted">Nunca</span>
        </template>

        <!-- Ações -->
        <template #cell(actions)="{ item }">
          <div class="d-flex gap-1">
            <BButton
              v-if="item.status !== 'offline'"
              size="sm"
              variant="outline-primary"
              @click="goToVMDetail(item.id)"
              :disabled="loading"
              title="Detalhes da VM"
            >
              <Icon name="camera" size="0.8rem" />
            </BButton>

            <BButton
              v-if="item.status === 'stopped' || item.status === 'error'"
              size="sm"
              variant="success"
              @click="startVM(item.id)"
              :disabled="loading || item.status === 'offline'"
              title="Iniciar VM"
            >
              <Icon name="play-fill" size="0.8rem" />
            </BButton>
            
            <BButton
              v-if="item.status === 'running'"
              size="sm"
              variant="warning"
              @click="stopVM(item.id)"
              :disabled="loading || item.status === 'offline'"
              title="Parar VM"
            >
              <Icon name="stop-fill" size="0.8rem" />
            </BButton>
            
            <BButton
              v-if="item.status === 'running' || item.status === 'error'"
              size="sm"
              variant="info"
              @click="restartVM(item.id)"
              :disabled="loading || item.status === 'offline'"
              title="Reiniciar VM"
            >
              <Icon name="arrow-clockwise" size="0.8rem" />
            </BButton>

            <BButton
              size="sm"
              variant="secondary"
              @click="promptDeleteVM(item)"
              :disabled="loading"
              title="Remover VM"
            >
              <Icon name="trash3-fill" size="0.8rem" style="color: #000;" />
            </BButton>
          </div>
        </template>

        <!-- Loading -->
        <template #table-busy>
          <div class="text-center my-4">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Carregando...</span>
            </div>
            <div class="mt-2">Carregando VMs...</div>
          </div>
        </template>
      </BTable>
    </div>

    
  </div>

  <!-- Modal de confirmação de exclusão -->
  <BModal v-model="showDeleteModal" title="Remover VM" hide-footer>
    <p>
      Tem certeza que deseja remover a VM
      <strong v-if="vmToDelete">{{ vmToDelete.name || vmToDelete.machine_id }}</strong>?
    </p>
    <p class="mb-2">
      Esta ação não afetará a VM em si. Apenas fará com que o orquestrador não monitore mais esta VM.
    </p>
    <div v-if="deleteError" class="text-danger mb-2">{{ deleteError }}</div>
    <div class="d-flex justify-content-end gap-2">
      <BButton variant="secondary" @click="showDeleteModal = false" :disabled="deleting">Cancelar</BButton>
      <BButton variant="danger" @click="confirmDeleteVM" :disabled="deleting">
        {{ deleting ? 'Removendo...' : 'Remover VM' }}
      </BButton>
    </div>
  </BModal>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Icon from '@/components/Icon.vue'
import { apiFetch } from '@/utils/http'
import {
  BTable,
  BFormInput,
  BFormSelect,
  BButton,
  BBadge,
  BRow,
  BCol,
  BModal
} from 'bootstrap-vue-3'
import { useRouter } from 'vue-router'

// Props e emits
const props = defineProps({
  refreshInterval: {
    type: Number,
    default: 30000
  }
})

const emit = defineEmits(['vm-action', 'refresh', 'error'])
const router = useRouter()

const goToVMDetail = (vmId) => {
  router.push(`/machines/${vmId}`)
}

// Estado reativo
const loading = ref(false)
const vms = ref([])
const searchQuery = ref('')
const statusFilter = ref('')
const connectionFilter = ref('')
const totalCount = ref(0)
const summary = ref({
  running: 0,
  stopped: 0,
  error: 0,
  offline: 0
})

// Opções dos filtros
const statusOptions = [
  { value: '', text: 'Todos os Status' },
  { value: 'running', text: 'Rodando' },
  { value: 'stopped', text: 'Parada' },
  { value: 'error', text: 'Erro' },
  { value: 'offline', text: 'Offline' }
]

const connectionOptions = [
  { value: '', text: 'Todas as Conexões' },
  { value: 'connected', text: 'Conectada' },
  { value: 'disconnected', text: 'Desconectada' }
]

// Campos da tabela
const tableFields = [
  { key: 'machine_id', label: 'ID da Máquina', sortable: true, class: 'text-monospace' },
  { key: 'name', label: 'Nome', sortable: true },
  { key: 'status', label: 'Status', sortable: true, class: 'text-center' },
  { key: 'mode', label: 'Modo', sortable: true, class: 'text-center' },
  { key: 'connection_status', label: 'Conexão', sortable: true, class: 'text-center' },
  { key: 'ip_address', label: 'IP', sortable: true, class: 'text-monospace' },
  { key: 'port', label: 'Porta', sortable: true, class: 'text-center' },
  { key: 'source_type', label: 'Fonte', sortable: true },
  { key: 'resolution', label: 'Resolução', sortable: false, class: 'text-center' },
  { key: 'fps', label: 'FPS', sortable: true, class: 'text-center' },
  { key: 'trigger_type', label: 'Trigger', sortable: true },
  { key: 'last_heartbeat', label: 'Último Heartbeat', sortable: true, class: 'text-center' },
  { key: 'actions', label: 'Ações', sortable: false, class: 'text-center' }
]

// Métodos
const fetchVMs = async () => {
  try {
    loading.value = true
    
    const params = new URLSearchParams()
    
    if (searchQuery.value) {
      params.append('search', searchQuery.value)
    }
    if (statusFilter.value) {
      params.append('status', statusFilter.value)
    }
    if (connectionFilter.value) {
      params.append('connection_status', connectionFilter.value)
    }
    
    const response = await apiFetch(`/api/vms?${params.toString()}`)
    if (!response.ok) {
      throw new Error('Erro ao buscar VMs')
    }
    
    const data = await response.json()
    vms.value = data.vms
    totalCount.value = data.total_count
  } catch (error) {
    console.error('Erro ao buscar VMs:', error)
    emit('error', error.message)
  } finally {
    loading.value = false
  }
}

const fetchStatusSummary = async () => {
  try {
    const response = await apiFetch('/api/vms/status/summary')
    if (response.ok) {
      const data = await response.json()
      summary.value = {
        running: data.status_counts?.running || 0,
        stopped: data.status_counts?.stopped || 0,
        error: data.status_counts?.error || 0,
        offline: (data.status_counts?.offline || (data.offline_vms?.length || 0))
      }
    }
  } catch (error) {
    console.error('Erro ao buscar resumo de status:', error)
  }
}

const handleSearch = () => {
  fetchVMs()
}

const handleFilterChange = () => {
  fetchVMs()
}

const refreshData = async () => {
  await Promise.all([fetchVMs(), fetchStatusSummary()])
  emit('refresh')
}

// Exclusão de VM
const showDeleteModal = ref(false)
const vmToDelete = ref(null)
const deleting = ref(false)
const deleteError = ref('')

const promptDeleteVM = (vm) => {
  vmToDelete.value = { id: vm.id, name: vm.name, machine_id: vm.machine_id }
  deleteError.value = ''
  showDeleteModal.value = true
}

const confirmDeleteVM = async () => {
  if (!vmToDelete.value) return
  try {
    deleting.value = true
    deleteError.value = ''
    await apiFetch(`/api/vms/${vmToDelete.value.id}`, { method: 'DELETE' })
    showDeleteModal.value = false
    await refreshData()
    emit('vm-action', { action: 'delete', vmId: vmToDelete.value.id, success: true })
  } catch (error) {
    deleteError.value = error.message
    emit('vm-action', { action: 'delete', vmId: vmToDelete.value?.id, success: false, error: error.message })
  } finally {
    deleting.value = false
    vmToDelete.value = null
  }
}

// Ações da VM
const startVM = async (vmId) => {
  try {
    loading.value = true
    const response = await apiFetch(`/api/vms/${vmId}/action`, {
      method: 'POST',
      body: JSON.stringify({ action: 'start' })
    })
    
    if (response.ok) {
      await refreshData()
      emit('vm-action', { action: 'start', vmId, success: true })
    } else {
      throw new Error('Erro ao iniciar VM')
    }
  } catch (error) {
    console.error('Erro ao iniciar VM:', error)
    emit('vm-action', { action: 'start', vmId, success: false, error: error.message })
  } finally {
    loading.value = false
  }
}

const stopVM = async (vmId) => {
  try {
    loading.value = true
    const response = await apiFetch(`/api/vms/${vmId}/action`, {
      method: 'POST',
      body: JSON.stringify({ action: 'stop' })
    })
    
    if (response.ok) {
      await refreshData()
      emit('vm-action', { action: 'stop', vmId, success: true })
    } else {
      throw new Error('Erro ao parar VM')
    }
  } catch (error) {
    console.error('Erro ao parar VM:', error)
    emit('vm-action', { action: 'stop', vmId, success: false, error: error.message })
  } finally {
    loading.value = false
  }
}

const restartVM = async (vmId) => {
  try {
    loading.value = true
    const response = await apiFetch(`/api/vms/${vmId}/action`, {
      method: 'POST',
      body: JSON.stringify({ action: 'restart' })
    })
    
    if (response.ok) {
      await refreshData()
      emit('vm-action', { action: 'restart', vmId, success: true })
    } else {
      throw new Error('Erro ao reiniciar VM')
    }
  } catch (error) {
    console.error('Erro ao reiniciar VM:', error)
    emit('vm-action', { action: 'restart', vmId, success: false, error: error.message })
  } finally {
    loading.value = false
  }
}

// Funções utilitárias
const getStatusVariant = (status) => {
  const variants = {
    'running': 'success',
    'stopped': 'warning',
    'error': 'danger',
    'offline': 'secondary'
  }
  return variants[status] || 'secondary'
}

const getStatusLabel = (status) => {
  const labels = {
    'running': 'Rodando',
    'stopped': 'Parada',
    'error': 'Erro',
    'offline': 'Offline'
  }
  return labels[status] || status
}

const getConnectionVariant = (status) => {
  const variants = {
    'connected': 'success',
    'disconnected': 'secondary'
  }
  return variants[status] || 'secondary'
}

const getConnectionLabel = (status) => {
  const labels = {
    'connected': 'Conectada',
    'disconnected': 'Desconectada'
  }
  return labels[status] || status
}

const getModeVariant = (mode) => {
  const variants = {
    'TESTE': 'info',
    'PRODUCAO': 'primary'
  }
  return variants[mode] || 'secondary'
}

const getModeLabel = (mode) => {
  const labels = {
    'TESTE': 'Teste',
    'PRODUCAO': 'Produção'
  }
  return labels[mode] || mode
}

const formatDateTime = (dateString) => {
  return new Date(dateString).toLocaleString('pt-BR')
}

const formatRelativeTime = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)
  
  if (diffMins < 1) return 'Agora'
  if (diffMins < 60) return `${diffMins}m atrás`
  if (diffHours < 24) return `${diffHours}h atrás`
  if (diffDays < 7) return `${diffDays}d atrás`
  
  return date.toLocaleDateString('pt-BR')
}

// Métodos expostos
const refresh = () => {
  refreshData()
}

// Expor métodos
defineExpose({
  refresh
})

// Lifecycle
onMounted(() => {
  refreshData()
  
  // Auto-refresh
  if (props.refreshInterval > 0) {
    setInterval(refreshData, props.refreshInterval)
  }
})
</script>

<style scoped>
.vms-table {
  background: white;
  border-radius: 8px;
  padding: 1rem;
}

.table-header {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.table-container {
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.status-summary {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 8px;
}

.status-row {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  grid-gap: 12px;
}

.status-col {
  min-width: 0;
}

/* Responsividade do painel: mantém em uma linha até atingir o mínimo, depois quebra para uma por linha */
@media (max-width: 1200px) {
  .status-row {
    grid-template-columns: repeat(5, minmax(160px, 1fr));
    overflow-x: auto;
    padding-bottom: 4px;
  }
}

@media (max-width: 768px) {
  .status-row {
    grid-template-columns: 1fr;
  }
}

.status-card {
  background: white;
  border-radius: 6px;
  border: 1px solid #dee2e6;
  transition: all 0.2s ease;
}

.status-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.status-number {
  font-size: 1.5rem;
  font-weight: bold;
  margin-bottom: 0.25rem;
}

.status-label {
  font-size: 0.875rem;
  color: #6c757d;
  font-weight: 500;
}

/* Responsividade */
@media (max-width: 768px) {
  .table-header .col-md-4,
  .table-header .col-md-3,
  .table-header .col-md-2 {
    margin-bottom: 0.5rem;
  }
  
  .status-summary .col-md-3 {
    margin-bottom: 1rem;
  }
}
</style>
