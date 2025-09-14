<template>
  <div>
    <TopMenu />
    <BContainer fluid class="mt-4">
      <BRow>
        <BCol cols="12">
          <BCard class="shadow-sm border-0">
            <BCardHeader class="text-white">
              <div class="d-flex align-items-center">
                <Icon name="clipboard-check" size="1.5rem" class="me-3" />
                <div>
                  <h2 class="mb-0">Log de Inspeções</h2>
                  <p class="mb-0 opacity-75">Registros das inspeções realizadas</p>
                </div>
              </div>
            </BCardHeader>
            <BCardBody class="p-4 p-md-5">
              <div class="d-flex justify-content-between align-items-center mb-3">
                <div class="d-flex align-items-center gap-2">
                  <Icon name="cpu" size="1.2rem" class="me-2" />
                  <strong>VMs online (conectadas)</strong>
                </div>
                <div class="d-flex gap-2">
                  <BButton variant="outline-primary" size="sm" @click="refresh" :disabled="loading">
                    <Icon name="arrow-clockwise" size="1rem" class="me-1" />
                    {{ loading ? 'Atualizando...' : 'Atualizar' }}
                  </BButton>
                </div>
              </div>

              <BAlert v-if="errorMessage" variant="danger" show class="mb-3">{{ errorMessage }}</BAlert>

              <BTable
                :items="tableItems"
                :fields="fields"
                :busy="loading"
                small
                hover
                responsive
                head-variant="light"
              >
                <template #table-busy>
                  <div class="text-center py-3">
                    Carregando...
                  </div>
                </template>
                <template #cell(actions)="{ item }">
                  <BButton size="sm" variant="secondary" @click="openLoggingModal(item)">
                    <Icon name="sliders" size="1rem" class="me-1" />
                    Configurar
                  </BButton>
                  <BButton size="sm" variant="outline-danger" class="ms-2" @click="openClearLogsModal(item)" :disabled="clearing">
                    <Icon name="trash" size="1rem" class="me-1" />
                    Limpar logs
                  </BButton>
                  <BButton size="sm" variant="outline-success" class="ms-2" @click="syncLogs(item)" :disabled="syncing">
                    <Icon name="cloud-download" size="1rem" class="me-1" />
                    Baixar logs
                  </BButton>
                </template>
              </BTable>

              <BModal v-model="showModal" title="Configuração de Logging" hide-footer>
                <div v-if="currentVM">
                  <div class="mb-3">
                    <label class="form-label">VM</label>
                    <div class="form-control" disabled>{{ currentVM.name }} ({{ currentVM.machine_id }})</div>
                  </div>
                  <div class="mb-3 form-check">
                    <input id="enabled" class="form-check-input" type="checkbox" v-model="form.enabled">
                    <label class="form-check-label" for="enabled">Ativar logging</label>
                  </div>

                  <div class="mb-3">
                    <label class="form-label">Modo</label>
                    <select class="form-select" v-model="form.mode">
                      <option value="keep_last">keep_last</option>
                      <option value="keep_first">keep_first</option>
                    </select>
                  </div>
                  <div class="mb-3">
                    <label class="form-label">Policy</label>
                    <select class="form-select" v-model="form.policy">
                      <option value="ALL">ALL</option>
                      <option value="APPROVED">APPROVED</option>
                      <option value="REJECTED">REJECTED</option>
                    </select>
                  </div>
                  <div class="row g-2">
                    <div class="col-6 mb-3">
                      <label class="form-label">Max Logs</label>
                      <input type="number" min="0" class="form-control" v-model.number="form.max_logs" />
                    </div>
                    <div class="col-6 mb-3">
                      <label class="form-label">Batch Size</label>
                      <input type="number" min="1" class="form-control" v-model.number="form.batch_size" />
                    </div>
                    <div class="col-6 mb-3">
                      <label class="form-label">Batch ms</label>
                      <input type="number" min="0" class="form-control" v-model.number="form.batch_ms" />
                    </div>
                  </div>

                  <div class="d-flex justify-content-end gap-2">
                    <BButton variant="secondary" @click="showModal = false">Cancelar</BButton>
                    <BButton variant="primary" :disabled="submitting" @click="submitLoggingConfig">
                      {{ submitting ? 'Salvando...' : 'Salvar' }}
                    </BButton>
                  </div>
                  <div v-if="modalError" class="text-danger mt-2">{{ modalError }}</div>
                </div>
              </BModal>

              <BModal v-model="showConfirmModal" title="Limpar logs da VM" hide-footer>
                <div v-if="vmToClear">
                  <p class="mb-3">
                    Tem certeza que deseja limpar todos os arquivos de log (.alog) da VM
                    <strong>{{ vmToClear.name }}</strong> ({{ vmToClear.machine_id }})?
                  </p>
                  <div class="d-flex justify-content-end gap-2">
                    <BButton variant="secondary" @click="showConfirmModal = false">Cancelar</BButton>
                    <BButton variant="danger" :disabled="clearing" @click="confirmClearLogs">
                      {{ clearing ? 'Limpando...' : 'Confirmar' }}
                    </BButton>
                  </div>
                </div>
              </BModal>
            </BCardBody>
          </BCard>
        </BCol>
      </BRow>

      <!-- Seção de Resultados de Inspeção -->
      <BRow class="mt-4">
        <BCol cols="12">
          <BCard class="shadow-sm border-0">
            <BCardHeader class="text-white">
              <div class="d-flex align-items-center">
                <Icon name="clipboard-list" size="1.5rem" class="me-3" />
                <div>
                  <h2 class="mb-0">Resultados de Inspeção</h2>
                  <p class="mb-0 opacity-75">Histórico de inspeções realizadas</p>
                </div>
              </div>
            </BCardHeader>
            <BCardBody class="p-4 p-md-5">
              <!-- Filtros -->
              <div class="row g-3 mb-4">
                <div class="col-md-3">
                  <label class="form-label">VM</label>
                  <select class="form-select" v-model="filters.vm_id" @change="fetchInspectionResults">
                    <option value="">Todas as VMs</option>
                    <option v-for="vm in vms" :key="vm.id" :value="vm.id">{{ vm.name }}</option>
                  </select>
                </div>
                <div class="col-md-3">
                  <label class="form-label">Data Inicial</label>
                  <input type="date" class="form-control" v-model="filters.start_date" @change="fetchInspectionResults" />
                </div>
                <div class="col-md-3">
                  <label class="form-label">Data Final</label>
                  <input type="date" class="form-control" v-model="filters.end_date" @change="fetchInspectionResults" />
                </div>
                <div class="col-md-3 d-flex align-items-end">
                  <BButton variant="outline-primary" @click="fetchInspectionResults" :disabled="loadingResults">
                    <Icon name="arrow-clockwise" size="1rem" class="me-1" />
                    {{ loadingResults ? 'Carregando...' : 'Atualizar' }}
                  </BButton>
                </div>
              </div>

              <BAlert v-if="resultsError" variant="danger" show class="mb-3">{{ resultsError }}</BAlert>

              <BTable
                :items="inspectionResults"
                :fields="resultFields"
                :busy="loadingResults"
                small
                hover
                responsive
                head-variant="light"
              >
                <template #table-busy>
                  <div class="text-center py-3">
                    Carregando resultados...
                  </div>
                </template>
                <template #cell(timestamp)="{ value }">
                  {{ formatDateTime(value) }}
                </template>
                <template #cell(approved)="{ value }">
                  <BBadge :variant="value ? 'success' : 'danger'">
                    {{ value ? 'Aprovado' : 'Rejeitado' }}
                  </BBadge>
                </template>
                <template #cell(image_url)="{ value, item }">
                  <div v-if="value" class="d-flex align-items-center">
                    <img 
                      :src="getImageUrl(value)" 
                      :alt="`Imagem ${item.cycle_id}`"
                      class="img-thumbnail me-2" 
                      style="width: 50px; height: 50px; object-fit: cover;"
                      @click="openImageModal(value, item)"
                    />
                    <small class="text-muted">{{ item.image_width }}x{{ item.image_height }}</small>
                  </div>
                  <span v-else class="text-muted">-</span>
                </template>
                <template #cell(actions)="{ item }">
                  <BButton size="sm" variant="outline-info" @click="viewDetails(item)">
                    <Icon name="eye" size="1rem" class="me-1" />
                    Detalhes
                  </BButton>
                </template>
              </BTable>
            </BCardBody>
          </BCard>
        </BCol>
      </BRow>

      <!-- Modal de Imagem -->
      <BModal v-model="showImageModal" :title="`Imagem - ${selectedItem?.cycle_id || ''}`" size="lg" hide-footer>
        <div v-if="selectedItem?.image_url" class="text-center">
          <img 
            :src="getImageUrl(selectedItem.image_url)" 
            :alt="`Imagem ${selectedItem.cycle_id}`"
            class="img-fluid"
            style="max-height: 70vh;"
          />
          <div class="mt-3">
            <small class="text-muted">
              Dimensões: {{ selectedItem.image_width }}x{{ selectedItem.image_height }} | 
              Tipo: {{ selectedItem.image_mime }}
            </small>
          </div>
        </div>
      </BModal>

      <!-- Modal de Detalhes da Inspeção -->
      <BModal v-model="showDetailsModal" :title="`Detalhes da Inspeção - ${selectedItem?.cycle_id || ''}`" size="xl" hide-footer>
        <div v-if="selectedItem">
          <!-- Informações básicas -->
          <div class="row mb-4">
            <div class="col-md-6">
              <h6 class="text-muted mb-2">Informações Básicas</h6>
              <table class="table table-sm">
                <tbody>
                  <tr>
                    <td><strong>VM:</strong></td>
                    <td>{{ selectedItem.vm_name }}</td>
                  </tr>
                  <tr>
                    <td><strong>Ciclo:</strong></td>
                    <td>{{ selectedItem.cycle_id }}</td>
                  </tr>
                  <tr>
                    <td><strong>Data/Hora:</strong></td>
                    <td>{{ formatDateTime(selectedItem.timestamp) }}</td>
                  </tr>
                  <tr>
                    <td><strong>Status:</strong></td>
                    <td>
                      <BBadge :variant="selectedItem.approved ? 'success' : 'danger'">
                        {{ selectedItem.approved ? 'Aprovado' : 'Rejeitado' }}
                      </BBadge>
                    </td>
                  </tr>
                  <tr>
                    <td><strong>Duração:</strong></td>
                    <td>{{ selectedItem.duration_ms }}ms</td>
                  </tr>
                  <tr>
                    <td><strong>Frame:</strong></td>
                    <td>{{ selectedItem.frame }}</td>
                  </tr>
                  <tr>
                    <td><strong>Reprovadas:</strong></td>
                    <td>{{ selectedItem.reprovadas }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div class="col-md-6">
              <h6 class="text-muted mb-2">Informações da Imagem</h6>
              <table class="table table-sm">
                <tbody>
                  <tr>
                    <td><strong>Dimensões:</strong></td>
                    <td>{{ selectedItem.image_width }}x{{ selectedItem.image_height }}</td>
                  </tr>
                  <tr>
                    <td><strong>Tipo:</strong></td>
                    <td>{{ selectedItem.image_mime || 'N/A' }}</td>
                  </tr>
                  <tr>
                    <td><strong>URL:</strong></td>
                    <td>
                      <small class="text-break">{{ getImageUrl(selectedItem.image_url) }}</small>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Componente AoVivoImg em modo readonly -->
          <div v-if="selectedItem.image_url" class="mb-4">
            <h6 class="text-muted mb-3">Análise Visual</h6>
            <div v-if="imageBinary" class="aovivo-container">
              <AoVivoImg
                :binary="imageBinary"
                :tools="getToolsFromResult()"
                :tool-defs="getToolDefsFromResult()"
                :metrics="getMetricsFromResult()"
                :results="getResultsFromResult()"
                :resolution="[selectedItem.image_width || 752, selectedItem.image_height || 480]"
                :read-only="true"
                aspect-ratio="16/9"
              />
            </div>
            <div v-else class="text-center py-4">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Carregando imagem...</span>
              </div>
              <p class="mt-2 text-muted">Carregando imagem para análise...</p>
            </div>
          </div>

          <!-- Dados JSON brutos (se disponível) -->
          <div v-if="selectedItem.result_json" class="mb-3">
            <h6 class="text-muted mb-2">Dados Técnicos (JSON)</h6>
            <pre class="bg-light p-3 rounded" style="max-height: 300px; overflow-y: auto; font-size: 0.8rem;">{{ JSON.stringify(selectedItem.result_json, null, 2) }}</pre>
          </div>
        </div>
      </BModal>
    </BContainer>
  </div>
  
</template>

<script setup>
import TopMenu from '@/components/TopMenu.vue'
import Icon from '@/components/Icon.vue'
import AoVivoImg from '@/components/AoVivoImg.vue'
import { ref, computed, onMounted } from 'vue'
import { apiFetch } from '@/utils/http'
import {
  BContainer,
  BRow,
  BCol,
  BCard,
  BCardHeader,
  BCardBody,
  BTable,
  BButton,
  BAlert,
  BBadge,
  BModal
} from 'bootstrap-vue-3'

const loading = ref(false)
const errorMessage = ref('')
const vms = ref([]) // lista detalhada, já com dados de logs
const showModal = ref(false)
const submitting = ref(false)
const modalError = ref('')
const currentVM = ref(null)
const clearing = ref(false)
const showConfirmModal = ref(false)
const vmToClear = ref(null)
const syncing = ref(false)

// Variáveis para resultados de inspeção
const loadingResults = ref(false)
const resultsError = ref('')
const inspectionResults = ref([])
const showImageModal = ref(false)
const showDetailsModal = ref(false)
const selectedItem = ref(null)
const imageBinary = ref(null)

const filters = ref({
  vm_id: '',
  start_date: '',
  end_date: ''
})

const form = ref({
  enabled: false,
  mode: 'keep_last',
  policy: 'ALL',
  max_logs: 1000,
  batch_size: 20,
  batch_ms: 500
})

const fields = [
  { key: 'name', label: 'VM' },
  { key: 'machine_id', label: 'ID' },
  { key: 'status', label: 'Status' },
  { key: 'connection_status', label: 'Conexão' },
  { key: 'logging_enabled', label: 'Logging' },
  { key: 'logs_count', label: 'Qtd. Logs' },
  { key: 'logging_buffer_size', label: 'Buffer' },
  { key: 'logging_mode', label: 'Modo' },
  { key: 'logging_max_logs', label: 'Max Logs' },
  { key: 'logging_policy', label: 'Policy' },
  { key: 'actions', label: 'Ações' }
]

const resultFields = [
  { key: 'vm_name', label: 'VM' },
  { key: 'cycle_id', label: 'Ciclo' },
  { key: 'timestamp', label: 'Data/Hora' },
  { key: 'approved', label: 'Status' },
  { key: 'image_url', label: 'Imagem' },
  { key: 'duration_ms', label: 'Duração (ms)' },
  { key: 'actions', label: 'Ações' }
]

const tableItems = computed(() =>
  vms.value.map(vm => ({
    name: vm.name || '-',
    machine_id: vm.machine_id || '-',
    status: vm.status || '-',
    connection_status: vm.connection_status || '-',
    logging_enabled: vm.logging_enabled ? 'Ativo' : 'Inativo',
    logs_count: typeof vm.logs_count === 'number' ? vm.logs_count : '-',
    logging_buffer_size: typeof vm.logging_buffer_size === 'number' ? vm.logging_buffer_size : '-',
    logging_mode: vm.logging_mode || '-',
    logging_max_logs: vm.logging_max_logs ?? '-',
    logging_policy: vm.logging_policy || '-'
  }))
)

async function fetchConnectedVMsWithLogs() {
  try {
    loading.value = true
    errorMessage.value = ''
    // 1) Buscar VMs conectadas
    const listRes = await apiFetch('/api/vms?connection_status=connected')
    if (!listRes.ok) {
      throw new Error(`Falha ao listar VMs (HTTP ${listRes.status})`)
    }
    const listData = await listRes.json()
    const list = Array.isArray(listData?.vms) ? listData.vms : []

    // 2) Buscar detalhes (para trazer campos de logging)
    const detailPromises = list.map(async (it) => {
      const res = await apiFetch(`/api/vms/${it.id}`)
      if (res.ok) {
        const det = await res.json()
        return det
      }
      return it
    })
    vms.value = await Promise.all(detailPromises)
  } catch (e) {
    errorMessage.value = e.message || 'Erro ao carregar VMs'
    vms.value = []
  } finally {
    loading.value = false
  }
}

function refresh() {
  fetchConnectedVMsWithLogs()
}

onMounted(() => {
  fetchConnectedVMsWithLogs()
  fetchInspectionResults()
})

function openLoggingModal(item) {
  // Encontrar VM completa (com id) a partir do machine_id/nome
  const vm = vms.value.find(v => v.machine_id === item.machine_id)
  if (!vm) return
  currentVM.value = vm
  form.value = {
    enabled: !!vm.logging_enabled,
    mode: vm.logging_mode || 'keep_last',
    policy: vm.logging_policy || 'ALL',
    max_logs: vm.logging_max_logs ?? 1000,
    batch_size: vm.logging_batch_size ?? 20,
    batch_ms: vm.logging_batch_ms ?? 500
  }
  modalError.value = ''
  showModal.value = true
}

async function submitLoggingConfig() {
  if (!currentVM.value) return
  try {
    submitting.value = true
    modalError.value = ''
    const payload = {
      enabled: !!form.value.enabled,
      mode: String(form.value.mode || 'keep_last'),
      policy: String(form.value.policy || 'ALL'),
      max_logs: Number(form.value.max_logs ?? 1000),
      batch_size: Number(form.value.batch_size ?? 20),
      batch_ms: Number(form.value.batch_ms ?? 500)
    }
    const res = await apiFetch(`/api/vms/${currentVM.value.id}/logging_config`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err?.erro || `Falha ao salvar (HTTP ${res.status})`)
    }
    // Atualizar tabela
    showModal.value = false
    await fetchConnectedVMsWithLogs()
  } catch (e) {
    modalError.value = e.message || 'Erro ao salvar configuração'
  } finally {
    submitting.value = false
  }
}

function openClearLogsModal(item) {
  const vm = vms.value.find(v => v.machine_id === item.machine_id)
  if (!vm) return
  vmToClear.value = vm
  showConfirmModal.value = true
}

async function confirmClearLogs() {
  if (!vmToClear.value) return
  try {
    clearing.value = true
    const res = await apiFetch(`/api/vms/${vmToClear.value.id}/clear_logs`, { method: 'POST' })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err?.erro || `Falha ao limpar (HTTP ${res.status})`)
    }
    showConfirmModal.value = false
    vmToClear.value = null
    await fetchConnectedVMsWithLogs()
  } catch (e) {
    alert(e.message || 'Erro ao limpar logs')
  } finally {
    clearing.value = false
  }
}

async function syncLogs(item) {
  try {
    const vm = vms.value.find(v => v.machine_id === item.machine_id)
    if (!vm) return
    syncing.value = true
    const res = await apiFetch(`/api/vms/${vm.id}/sync_logs`, { method: 'POST' })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err?.erro || `Falha ao baixar (HTTP ${res.status})`)
    }
    await fetchConnectedVMsWithLogs()
  } catch (e) {
    alert(e.message || 'Erro ao baixar logs')
  } finally {
    syncing.value = false
  }
}

// Funções para resultados de inspeção
async function fetchInspectionResults() {
  try {
    loadingResults.value = true
    resultsError.value = ''
    
    const params = new URLSearchParams()
    if (filters.value.vm_id) params.append('vm_id', filters.value.vm_id)
    if (filters.value.start_date) params.append('start_date', filters.value.start_date)
    if (filters.value.end_date) params.append('end_date', filters.value.end_date)
    
    const url = `/api/inspection-results${params.toString() ? '?' + params.toString() : ''}`
    const res = await apiFetch(url)
    
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err?.erro || `Falha ao buscar resultados (HTTP ${res.status})`)
    }
    
    const data = await res.json()
    inspectionResults.value = data.data || []
  } catch (e) {
    resultsError.value = e.message || 'Erro ao carregar resultados'
    inspectionResults.value = []
  } finally {
    loadingResults.value = false
  }
}

function formatDateTime(isoString) {
  if (!isoString) return '-'
  try {
    const date = new Date(isoString)
    return date.toLocaleString('pt-BR', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  } catch {
    return isoString
  }
}

function getImageUrl(imageUrl) {
  if (!imageUrl) return ''
  // Se já é uma URL completa, retorna como está
  if (imageUrl.startsWith('http')) return imageUrl
  // Se é um caminho relativo, adiciona o host do backend
  const baseUrl = window.location.origin.includes('5173') 
    ? 'http://localhost:8000' 
    : window.location.origin
  return `${baseUrl}${imageUrl}`
}

function openImageModal(imageUrl, item) {
  selectedItem.value = item
  showImageModal.value = true
}

async function viewDetails(item) {
  selectedItem.value = item
  imageBinary.value = null // Reset binary data
  showDetailsModal.value = true
  
  // Carregar imagem como binário se houver URL
  if (item.image_url) {
    await loadImageAsBinary(item.image_url)
  }
}

// Funções para mapear dados do result_json para o formato esperado pelo AoVivoImg
function getToolsFromResult() {
  const result = selectedItem.value?.result_json
  if (!result) return []
  
  // O JSON do VM agora tem 'tools' (configuração) e 'result' (resultados)
  // Para o AoVivoImg, precisamos dos resultados das ferramentas
  const toolsResults = result.result || result.tools || []
  
  return toolsResults.map(tool => ({
    order_index: tool.order_index || 0,
    name: tool.name || '',
    type: tool.type || '',
    ROI: tool.ROI || {},
    inspec_pass_fail: tool.inspec_pass_fail || false,
    ...tool // Incluir todas as outras propriedades específicas do tipo de ferramenta
  }))
}

function getToolDefsFromResult() {
  const result = selectedItem.value?.result_json
  if (!result) return []
  
  // O JSON do VM tem 'tools' que contém a configuração das ferramentas
  return result.tools || []
}

function getMetricsFromResult() {
  const result = selectedItem.value?.result_json
  if (!result) {
    return {
      aprovados: selectedItem.value?.approved ? 1 : 0,
      reprovados: selectedItem.value?.approved ? 0 : 1,
      time: (selectedItem.value?.duration_ms || 0) + 'ms',
      frame: selectedItem.value?.frame || 0
    }
  }
  
  // Usar dados do JSON do VM (agora com aprovados/reprovados calculados)
  return {
    aprovados: result.aprovados || 0,
    reprovados: result.reprovados || 0,
    time: result.time || ((selectedItem.value?.duration_ms || 0) + 'ms'),
    frame: result.frame || selectedItem.value?.frame || 0
  }
}

function getResultsFromResult() {
  const result = selectedItem.value?.result_json
  if (!result) return []
  
  // O JSON do VM tem 'result' que contém os resultados das ferramentas
  const toolsResults = result.result || []
  
  return toolsResults.map(tool => ({
    tool_name: tool.name || '',
    tool_id: tool.order_index || 0,
    tool_type: tool.type || '',
    inspec_pass_fail: tool.inspec_pass_fail || false,
    ROI: tool.ROI || {},
    // Incluir dados específicos da ferramenta
    ...tool
  }))
}

async function loadImageAsBinary(imageUrl) {
  try {
    const fullUrl = getImageUrl(imageUrl)
    const response = await fetch(fullUrl)
    
    if (!response.ok) {
      throw new Error(`Erro ao carregar imagem: ${response.status}`)
    }
    
    const blob = await response.blob()
    
    // Converter blob para ArrayBuffer
    const arrayBuffer = await blob.arrayBuffer()
    
    // Converter para Uint8Array (formato esperado pelo AoVivoImg)
    imageBinary.value = new Uint8Array(arrayBuffer)
    
  } catch (error) {
    console.error('Erro ao carregar imagem:', error)
    // Em caso de erro, tentar usar a URL diretamente como fallback
    imageBinary.value = imageUrl
  }
}
</script>

<style scoped>
/* Gradiente consistente com o padrão das demais páginas */
.card-header {
  background: linear-gradient(135deg, #6c757d 0%, #495057 100%) !important; /* cinza (secondary) */
}

.opacity-75 { opacity: 0.75; }

/* Responsividade básica para manter consistência */
@media (max-width: 768px) {
  .p-md-5 {
    padding: 1rem !important;
  }
}

/* Estilos para o container do AoVivoImg */
.aovivo-container {
  border: 1px solid #e9ecef;
  border-radius: 8px;
  overflow: hidden;
  background: #f8f9fa;
}

.aovivo-container .aovivoimg {
  background: white;
}
</style>


