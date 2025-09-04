<template>
  <div>
    <TopMenu />
    <BContainer fluid class="mt-4">
      <BRow>
        <BCol cols="12">
          <BCard class="shadow-sm border-0">
            <BCardHeader class="bg-info text-white">
              <div class="d-flex align-items-center justify-content-between">
                <div class="d-flex align-items-center">
                  <Icon name="camera" size="1.5rem" class="me-3" />
                  <div>
                    <h2 class="mb-0">Máquina de Visão (Detalhes)</h2>
                    <p class="mb-0 opacity-75">Informações completas da VM selecionada</p>
                  </div>
                </div>
                <BButton variant="danger" size="sm" class="text-white" @click="goBack">x</BButton>
              </div>
            </BCardHeader>
            <BCardBody class="p-4 p-md-5">
              <div v-if="loading" class="text-muted">Carregando...</div>
              <div v-else-if="error" class="text-danger">{{ error }}</div>
              <div v-else>
                <div v-if="vm" class="mb-4">
                  <div class="d-flex align-items-start justify-content-between flex-wrap gap-2">
                    <div class="me-3">
                      <h3 class="mb-1">{{ vm.name || vm.machine_id }}</h3>
                      <div class="text-muted small">ID: <span class="text-monospace">{{ vm.machine_id }}</span></div>
                    </div>
                    <div class="d-flex align-items-center gap-2">
                      <BBadge :variant="getStatusVariant(vm.status)">{{ getStatusLabel(vm.status) }}</BBadge>
                      <BBadge :variant="getConnectionVariant(vm.connection_status)">{{ getConnectionLabel(vm.connection_status) }}</BBadge>
                      <BBadge :variant="getModeVariant(vm.mode)">{{ getModeLabel(vm.mode) }}</BBadge>
                    </div>
                  </div>

                  <hr class="my-4" />

                  <BRow class="g-3">
                    <BCol cols="12" md="4">
                      <div class="kv-label">Endereço</div>
                      <div class="kv-value text-monospace">{{ (vm.ip_address || '—') + (vm.port ? ':' + vm.port : '') }}</div>
                    </BCol>
                    <BCol cols="12" md="4">
                      <div class="kv-label">Fonte</div>
                      <div class="kv-value">{{ vm.source_type || '—' }}</div>
                    </BCol>
                    <BCol cols="12" md="4">
                      <div class="kv-label">Resolução</div>
                      <div class="kv-value text-monospace">{{ vm.resolution || (vm.resolution_width && vm.resolution_height ? `${vm.resolution_width}x${vm.resolution_height}` : '—') }}</div>
                    </BCol>

                    <BCol cols="12" md="4">
                      <div class="kv-label">FPS</div>
                      <div class="kv-value">{{ vm.fps ?? '—' }}</div>
                    </BCol>
                    <BCol cols="12" md="4">
                      <div class="kv-label">Trigger</div>
                      <div class="kv-value">{{ vm.trigger_type || '—' }}<span v-if="vm.trigger_interval_ms"> ({{ vm.trigger_interval_ms }} ms)</span></div>
                    </BCol>
                    <BCol cols="12" md="4">
                      <div class="kv-label">Último Heartbeat</div>
                      <div class="kv-value">{{ formatDateTime(vm.last_heartbeat) }}</div>
                    </BCol>

                    <BCol cols="12" md="6" v-if="vm.django_url">
                      <div class="kv-label">Endpoint Django</div>
                      <div class="kv-value text-break">{{ vm.django_url }}</div>
                    </BCol>
                    <BCol cols="12" md="6" v-if="vm.error_message">
                      <div class="kv-label text-danger">Mensagem de Erro</div>
                      <div class="kv-value text-danger">{{ vm.error_message }}</div>
                    </BCol>
                  </BRow>
                </div>

                <!-- Visualização ao vivo -->
                <div class="mt-4">
                  <div class="d-flex align-items-center justify-content-between mb-3">
                    <h4 class="mb-0">Transmissão ao vivo</h4>
                    <div class="d-flex align-items-center gap-2 flex-wrap">
                      <div v-if="wsStatus">
                        <BBadge :variant="getWsVariant(wsStatus)">{{ wsStatus }}</BBadge>
                      </div>
                      <div class="d-flex gap-1 align-items-center">
                        <BButton size="sm" variant="outline-success" :disabled="vmActionLoading" @click="vmCommand('start')">Start</BButton>
                        <BButton size="sm" variant="outline-warning" :disabled="vmActionLoading" @click="vmCommand('stop')">Stop</BButton>
                        <BButton size="sm" variant="outline-secondary" :disabled="vmActionLoading" @click="vmCommand('restart')">Restart</BButton>
                        <BButton size="sm" variant="outline-primary" :disabled="vmActionLoading || triggerDisabled" @click="vmCommand('trigger')">Trigger</BButton>
                      </div>
                      <BButton
                        size="sm"
                        variant="primary"
                        :disabled="!canSaveInspection"
                        @click="openSaveModal"
                      >
                        Salvar receita
                      </BButton>
                    </div>
                  </div>
                  <BRow class="live-row g-3">
                    <BCol cols="12" lg="12">
                      <AoVivoImg
                        :binary="liveFrame"
                        :mime-type="liveMime"
                        :ratio="liveRatio"
                        :results="liveTools"
                        :tool-defs="liveToolDefs"
                        :resolution="liveResolution"
                        :metrics="metrics"
                        fit="contain"
                      />
                      
                    </BCol>
                  </BRow>
                </div>

                <!-- Painel JSON no final da página -->
                <div class="mt-4">
                  <h4 class="mb-2">Último JSON recebido</h4>
                  <BFormTextarea
                    v-model="wsJsonText"
                    class="json-textarea"
                    rows="14"
                    readonly
                    placeholder="Aguardando dados..."
                  />
                </div>
              </div>
            </BCardBody>
          </BCard>
        </BCol>
      </BRow>
    </BContainer>
  </div>
  
  <!-- Modal: Salvar Inspeção -->
  <BModal v-model="showSaveModal" title="Salvar inspeção" ok-only :ok-disabled="saveLoading" @ok="doSaveInspection(false)">
    <BFormGroup label="Nome da inspeção" label-for="insp-name">
      <BFormInput id="insp-name" v-model="saveName" :disabled="saveLoading" placeholder="Ex.: Inspeção Linha 1" />
    </BFormGroup>
  </BModal>

  <!-- Modal: Confirmar Sobrescrita -->
  <BModal v-model="showConfirmModal" title="Inspeção já existe" :ok-disabled="saveLoading" @ok="doSaveInspection(true)" ok-title="Sobrescrever" cancel-title="Cancelar">
    Já existe uma inspeção com este nome. Deseja sobrescrever?
  </BModal>

  <!-- Toasts -->
  <div class="position-fixed top-0 end-0 p-3" style="z-index: 1080;">
    <BToast v-model="showSuccessToast" :title="toastTitle" variant="success" solid auto-hide-delay="3000">
      {{ toastMsg }}
    </BToast>
    <BToast v-model="showErrorToast" :title="toastTitle" variant="danger" solid auto-hide-delay="5000">
      {{ toastMsg }}
    </BToast>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import TopMenu from '@/components/TopMenu.vue'
import Icon from '@/components/Icon.vue'
import AoVivoImg from '@/components/AoVivoImg.vue'
import { apiFetch } from '@/utils/http'
import { BContainer, BButton, BCard, BCardBody } from 'bootstrap-vue-3'
import { BCardHeader, BRow, BCol } from 'bootstrap-vue-3'
import { BFormTextarea } from 'bootstrap-vue-3'
import { BBadge } from 'bootstrap-vue-3'
import { BModal } from 'bootstrap-vue-3'
import { BFormInput, BFormGroup } from 'bootstrap-vue-3'
import { io } from 'socket.io-client'

const route = useRoute()
const router = useRouter()

const vm = ref(null)
const loading = ref(false)
const error = ref('')
const liveFrame = ref(null)
const liveMime = ref('image/jpeg')
const liveRatio = ref('16/9')
const wsStatus = ref('')
const wsJsonText = ref('')
const liveTools = ref([])
const liveToolDefs = ref([])
const liveResolution = ref([])
const metrics = ref({ aprovados: 0, reprovados: 0, time: '', frame: 0 })
let sio = null
// Controle do modal de salvar inspeção
const showSaveModal = ref(false)
const showConfirmModal = ref(false)
const saveName = ref('')
const saveLoading = ref(false)
const showSuccessToast = ref(false)
const showErrorToast = ref(false)
const toastTitle = ref('')
const toastMsg = ref('')
const vmActionLoading = ref(false)
const triggerDisabled = computed(() => String(vm.value?.trigger_type || '').toLowerCase() !== 'trigger')

const canSaveInspection = computed(() => {
  const s = (wsStatus.value || '').toLowerCase()
  return s.includes('conectado')
})

function openSaveModal() {
  saveName.value = vm.value?.name || vm.value?.machine_id || ''
  showSaveModal.value = true
}

async function doSaveInspection(overwrite = false) {
  if (!vm.value) return
  try {
    saveLoading.value = true
    // Tentar incluir o último JSON recebido como payload
    let payload
    try { payload = wsJsonText.value ? JSON.parse(wsJsonText.value) : undefined } catch { payload = undefined }
    const res = await apiFetch(`/api/vms/${vm.value.id}/inspections/save`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: saveName.value,
        overwrite,
        payload: {
          ...payload,
          image_base64: liveFrame.value || payload?.image_base64,
          mime: liveMime.value || payload?.mime,
          resolution: Array.isArray(liveResolution.value) && liveResolution.value.length === 2 ? liveResolution.value : payload?.resolution
        }
      }),
      okStatuses: [200, 201, 409]
    })
    if (res.status === 409) {
      // Já existe: pedir confirmação de overwrite
      showConfirmModal.value = true
      return
    }
    if (!res.ok) {
      const err = await res.json().catch(() => ({ erro: 'Erro desconhecido' }))
      throw new Error(err?.erro || 'Falha ao salvar inspeção')
    }
    // Sucesso
    showSaveModal.value = false
    showConfirmModal.value = false
    toastTitle.value = 'Sucesso'
    toastMsg.value = 'Inspeção salva com sucesso'
    showSuccessToast.value = true
  } catch (e) {
    console.error('save inspection error', e)
    toastTitle.value = 'Erro'
    toastMsg.value = e?.message || 'Erro ao salvar inspeção'
    showErrorToast.value = true
  } finally {
    saveLoading.value = false
  }
}

// Oculta campos binários no painel de JSON
const jsonReplacer = (key, value) => {
  if (key === 'image_base64' || key === 'final_image') return '[hidden]'
  return value
}



const goBack = () => {
  router.push('/machines')
}

const loadVM = async () => {
  try {
    loading.value = true
    error.value = ''
    const id = route.params.id
    const res = await apiFetch(`/api/vms/${id}`)
    const data = await res.json()
    vm.value = data
  } catch (e) {
    error.value = e.message || 'Erro ao carregar VM'
  } finally {
    loading.value = false
  }
}

onMounted(loadVM)
async function vmCommand(action) {
  if (!vm.value?.id) return
  try {
    vmActionLoading.value = true
    const res = await apiFetch(`/api/vms/${vm.value.id}/action`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action })
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({ erro: 'Falha ao executar comando' }))
      throw new Error(err?.erro || 'Falha ao executar comando')
    }
    // Recarregar dados da VM após ação (exceto para trigger)
    if (action !== 'trigger') {
      await loadVM()
    }
  } catch (e) {
    console.error('vm action error', e)
    toastTitle.value = 'Erro'
    toastMsg.value = e?.message || 'Erro ao executar comando'
    showErrorToast.value = true
  } finally {
    vmActionLoading.value = false
  }
}

function connectWebSocket() {
  if (!vm.value) return
  try {
    // Monta a URL do WebSocket da VM
    // Preferência: usar ip:port, senão tentar django_url
    let host = ''
    if (vm.value.ip_address && vm.value.port) {
      host = `${vm.value.ip_address}:${vm.value.port}`
    } else if (vm.value.django_url) {
      try {
        const u = new URL(vm.value.django_url)
        host = u.host
      } catch {
        // fallback mantém vazio
      }
    }
    if (!host) {
      wsStatus.value = 'Sem endpoint de WebSocket disponível'
      return
    }

    const httpProtocol = location.protocol === 'https:' ? 'https' : 'http'
    const sioUrl = `${httpProtocol}://${host}`
    wsStatus.value = 'Conectando...'
    // Conectar com Socket.IO (compatível com Flask-SocketIO)
    sio = io(sioUrl, { transports: ['websocket', 'polling'] })

    sio.on('connect', () => {
      wsStatus.value = 'Conectado'
    })

    sio.on('disconnect', () => {
      wsStatus.value = 'Desconectado'
    })

    // Eventos emitidos pela VM
    sio.on('connected', (data) => {
      wsJsonText.value = JSON.stringify(data, jsonReplacer, 2)
    })

    sio.on('test_result', (data) => {
      wsJsonText.value = JSON.stringify(data, jsonReplacer, 2)
      if (data && data.image_base64) {
        liveMime.value = data.mime || 'image/jpeg'
        liveFrame.value = data.image_base64
        if (Array.isArray(data.resolution) && data.resolution.length === 2) {
          liveRatio.value = `${data.resolution[0]}/${data.resolution[1]}`
          liveResolution.value = data.resolution
        }
      }
      if (Array.isArray(data?.result)) {
        liveTools.value = data.result
      } else if (Array.isArray(data?.tools)) {
        liveTools.value = data.tools
      }
      // manter definições das tools para extrair ROI quando resultados não tiverem
      if (Array.isArray(data?.tools)) {
        liveToolDefs.value = data.tools
      }
      metrics.value = {
        aprovados: data?.aprovados,
        reprovados: data?.reprovados,
        time: data?.time,
        frame: data?.frame
      }
    })

    sio.on('inspection_result', (payload) => {
      wsJsonText.value = JSON.stringify(payload, jsonReplacer, 2)
    })
  } catch {
    wsStatus.value = 'Falha ao conectar'
  }
}

// Recalcula razão quando resolução conhecida
watch(vm, (v) => {
  if (!v) return
  if (v.resolution_width && v.resolution_height) {
    liveRatio.value = `${v.resolution_width}/${v.resolution_height}`
  }
  connectWebSocket()
})

onBeforeUnmount(() => {
  if (!sio) return
  try { sio.disconnect() } catch (err) { console.debug('sio disconnect error', err) }
  sio = null
})


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
  if (!dateString) return '—'
  try {
    return new Date(dateString).toLocaleString('pt-BR')
  } catch {
    return String(dateString)
  }
}

const getWsVariant = (status) => {
  const s = String(status || '').toLowerCase().trim()
  // Priorizar estados de erro/desconexão para evitar colisão com 'conectado'
  if (s.includes('desconect') || s.includes('falha') || s.includes('fail') || s.includes('disconnected')) return 'danger'
  if (s.includes('conectand') || s.includes('connecting')) return 'warning'
  if (s === 'conectado' || s.includes('conectado') || s.includes('connected')) return 'success'
  return 'secondary'
}
</script>

<style scoped>
.bg-info {
  background: linear-gradient(135deg, #17a2b8 0%, #138496 100%) !important;
}

.opacity-75 {
  opacity: 0.75;
}

.kv-label {
  font-size: 0.75rem;
  color: #6c757d;
  text-transform: uppercase;
  letter-spacing: .04em;
}

.kv-value {
  font-size: 1rem;
}

.live-row .aovivoimg .frame-wrapper {
  /* Garante altura confortável ao lado do textarea */
  min-height: 320px;
}

.json-textarea {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  background: #0b1520;
  color: #cfe8ff;
  border: 1px solid #153047;
  border-radius: 8px;
}

.metrics-panel {
  border: 1px solid #e9ecef;
  border-radius: 10px;
  background: #fff;
}

.metrics-header {
  font-weight: 600;
  padding: 10px 12px;
  border-bottom: 1px solid #e9ecef;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  padding: 10px 12px;
}

.metric {
  border: 1px solid #f1f3f5;
  border-radius: 8px;
  padding: 8px;
  background: #f8f9fa;
}

.metric .label {
  font-size: 0.8rem;
  color: #6c757d;
}

.metric .value {
  font-weight: 700;
}

.tool-details .tools-header {
  font-weight: 600;
  padding: 10px 12px;
  border: 1px solid #e9ecef;
  border-radius: 10px 10px 0 0;
  background: #fff;
}

.tool-details .tool-json {
  margin: 0;
  border: 1px solid #e9ecef;
  border-top: 0;
  border-radius: 0 0 10px 10px;
  background: #0b1520;
  color: #cfe8ff;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  padding: 10px 12px;
  max-height: 300px;
  overflow: auto;
}
</style>


