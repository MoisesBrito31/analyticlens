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
                  <img :src="getImagePath('icons/pencil-square.svg')" alt="Editar" style="width:1.5rem;height:1.5rem" class="me-3" />
                  <div>
                    <h2 class="mb-0">Edição de inspeção (ao vivo)</h2>
                    <p class="mb-0 opacity-75">VM #{{ route.params.id }} • ajuste de configurações em tempo real</p>
                  </div>
                </div>
                <div class="d-flex align-items-center gap-2">
                  <BButton variant="outline-secondary" size="sm" @click="goBack">Voltar</BButton>
                </div>
              </div>
            </BCardHeader>
            <BCardBody class="p-4 p-md-5">
              <div v-if="loading" class="text-muted">Carregando...</div>
              <div v-else-if="error" class="text-danger">{{ error }}</div>
              <div v-else>
                <!-- Ao Vivo -->
                <div class="mb-4">
                  <div class="d-flex align-items-center justify-content-between mb-3">
                    <h4 class="mb-0">Transmissão ao vivo</h4>
                    <div class="d-flex align-items-center gap-2 flex-wrap">
                      <div v-if="wsStatus" class="badge bg-secondary">{{ wsStatus }}</div>
                      <div v-if="vm?.status" :class="['badge', vmStatusBadgeClass]">{{ vmStatusLabel }}</div>
                      <div v-if="vm?.mode" :class="['badge', vmModeBadgeClass]">{{ vmModeLabel }}</div>
                      <div class="d-flex gap-1 align-items-center">
                        <BButton size="sm" variant="outline-success" :disabled="vmActionLoading" @click="vmCommand('start')">Start</BButton>
                        <BButton size="sm" variant="outline-warning" :disabled="vmActionLoading" @click="vmCommand('stop')">Stop</BButton>
                        <BButton size="sm" variant="outline-secondary" :disabled="vmActionLoading" @click="vmCommand('restart')">Restart</BButton>
                        <BButton size="sm" variant="outline-primary" :disabled="vmActionLoading || String(liveTrigger.type||'').toLowerCase() !== 'trigger'" @click="vmCommand('trigger')">Trigger</BButton>
                      </div>
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
                        :tools="toolsItems"
                        :resolution="liveResolution"
                        :metrics="metrics"
                        :editable="true"
                        :read-only="false"
                        fit="contain"
                        @select="onSelectTool"
                        @update-tool-roi="onUpdateToolRoi"
                        @update-tool-param="onUpdateToolParam"
                        @update-inspection-config="onUpdateInspectionConfig"
                      />
                    </BCol>
                  </BRow>
                </div>

                <div class="mb-3">
                  <BFormGroup label="Inspeção alvo">
                    <BFormSelect v-model="selectedInspectionId" :options="inspectionOptions" :disabled="loadingInspections" />
                  </BFormGroup>
                </div>
                <BRow class="g-3">
                  <BCol cols="12" md="6">
                    <h5 class="mb-2">Source</h5>
                    <BFormGroup label="Tipo">
                      <BFormSelect :options="sourceTypeOptions" v-model="liveSource.type" @change="scheduleApplyToVM()" />
                    </BFormGroup>
                    <BFormGroup v-if="String(liveSource.type||'').toLowerCase() === 'pasta'" label="Pasta (folder_path)">
                      <div class="d-flex gap-2 align-items-center">
                        <BFormInput type="text" v-model="liveSource.folder_path" placeholder="Ex.: ./images" />
                        <BButton size="sm" variant="primary" @click="applyFolderPath">Atualizar</BButton>
                      </div>
                    </BFormGroup>
                    <BFormGroup v-if="String(liveSource.type||'').toLowerCase() === 'camera'" label="ID da Câmera (camera_id)">
                      <BFormInput type="number" min="0" v-model.number="liveSource.camera_id" @input="scheduleApplyToVM()" />
                    </BFormGroup>
                    <BFormGroup v-if="String(liveSource.type||'').toLowerCase() === 'rtsp'" label="RTSP URL">
                      <BFormInput type="text" v-model="liveSource.rtsp_url" @input="scheduleApplyToVM()" placeholder="rtsp://..." />
                    </BFormGroup>
                    <BFormGroup label="FPS">
                      <BFormInput type="number" min="1" max="120" v-model.number="liveSource.fps" @input="scheduleApplyToVM()" />
                    </BFormGroup>
                    <div class="d-flex gap-2">
                      <BFormGroup label="Largura" class="flex-fill">
                        <BFormInput type="number" min="1" v-model.number="liveResolutionWidth" @input="scheduleApplyToVM()" />
                      </BFormGroup>
                      <BFormGroup label="Altura" class="flex-fill">
                        <BFormInput type="number" min="1" v-model.number="liveResolutionHeight" @input="scheduleApplyToVM()" />
                      </BFormGroup>
                    </div>
                  </BCol>
                  <BCol cols="12" md="6">
                    <h5 class="mb-2">Trigger</h5>
                    <BFormGroup label="Tipo">
                      <BFormSelect :options="triggerTypeOptions" v-model="liveTrigger.type" @change="onTriggerTypeChange" />
                    </BFormGroup>
                    <BFormGroup label="Intervalo (ms)" v-if="String(liveTrigger.type||'').toLowerCase() === 'continuous'">
                      <BFormInput type="number" min="1" v-model.number="liveTrigger.interval_ms" @input="scheduleApplyToVM()" />
                    </BFormGroup>
                  </BCol>
                </BRow>

                <div v-if="liveError" class="text-danger mt-3">{{ liveError }}</div>
              </div>
            </BCardBody>
          </BCard>
        </BCol>
      </BRow>
    </BContainer>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onBeforeUnmount, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import TopMenu from '@/components/TopMenu.vue'
import getImagePath from '@/utils/imageRouter.js'
import { apiFetch } from '@/utils/http'
import { io } from 'socket.io-client'
import { BContainer, BRow, BCol, BCard, BCardHeader, BCardBody, BButton } from 'bootstrap-vue-3'
import { BFormGroup, BFormSelect, BFormInput } from 'bootstrap-vue-3'
import AoVivoImg from '@/components/AoVivoImg.vue'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const error = ref('')
const loadingInspections = ref(false)
const inspectionOptions = ref([])
const selectedInspectionId = ref(null)
const liveSource = ref({ type: '', folder_path: '', camera_id: null, rtsp_url: '', fps: null })
const liveResolutionWidth = ref(null)
const liveResolutionHeight = ref(null)
const liveTrigger = ref({ type: '', interval_ms: null })
const sourceTypeOptions = [
  { value: 'pasta', text: 'Pasta' },
  { value: 'camera', text: 'Câmera Local' },
  { value: 'picamera2', text: 'Raspberry Pi (Picamera2)' },
  { value: 'rtsp', text: 'RTSP' }
]
const triggerTypeOptions = [
  { value: 'continuous', text: 'Contínuo' },
  { value: 'trigger', text: 'Trigger' }
]
const applyLoading = ref(false)
const liveError = ref('')

// Ao vivo / VM
const vm = ref(null)
const wsStatus = ref('')
const liveFrame = ref(null)
const liveMime = ref('image/jpeg')
const liveRatio = ref('16/9')
const liveTools = ref([])
const liveToolDefs = ref([])
// Quando true, prioriza a receita vinda da VM (WS) ao entrar na edição online
const vmConfigApplied = ref(false)
const liveResolution = ref([])
const metrics = ref({ aprovados: 0, reprovados: 0, time: '', frame: 0 })
let sio = null
const vmActionLoading = ref(false)

// Badges de estado e modo
const vmStatusLabel = computed(() => {
  const s = String(vm.value?.status || '').toLowerCase()
  if (s === 'running') return 'running'
  if (s === 'stopped') return 'idle'
  if (s === 'error') return 'erro'
  if (s) return s
  return ''
})
const vmStatusBadgeClass = computed(() => {
  const l = vmStatusLabel.value
  if (l === 'running') return 'bg-success text-white'
  if (l === 'idle') return 'bg-warning text-dark'
  if (l === 'erro') return 'bg-danger text-white'
  return 'bg-secondary text-white'
})
const vmModeLabel = computed(() => {
  const m = String(vm.value?.mode || '').toUpperCase()
  if (m === 'PRODUCAO') return 'RUN'
  if (m === 'TESTE') return 'TESTE'
  return m
})
const vmModeBadgeClass = computed(() => {
  const m = String(vm.value?.mode || '').toUpperCase()
  if (m === 'PRODUCAO') return 'bg-primary text-white'
  if (m === 'TESTE') return 'bg-info text-dark'
  return 'bg-secondary text-white'
})

function goBack() {
  router.push(`/machines/${route.params.id}`)
}

async function loadInitial() {
  try {
    loading.value = true
    liveError.value = ''
    // Carregar inspeções desta VM
    await loadInspectionsForVM(route.params.id)
    // Carregar VM e conectar WS
    await loadVM()
    connectWebSocket()
  } catch (e) {
    error.value = e?.message || 'Erro ao carregar dados'
  } finally {
    loading.value = false
  }
}

async function loadInspectionsForVM(vmId) {
  try {
    loadingInspections.value = true
    const res = await apiFetch(`/api/inspections?vm_id=${vmId}`)
    const data = await res.json()
    const list = Array.isArray(data?.inspections) ? data.inspections : []
    inspectionOptions.value = list.map((i) => ({ value: i.id, text: `${i.name} (ID ${i.id})` }))
    if (!selectedInspectionId.value && inspectionOptions.value.length > 0) {
      selectedInspectionId.value = inspectionOptions.value[0].value
    }
  } catch (e) {
    inspectionOptions.value = []
  } finally {
    loadingInspections.value = false
  }
}

// Carrega VM e prepara defaults dos campos
async function loadVM() {
  const id = route.params.id
  const res = await apiFetch(`/api/vms/${id}`)
  const data = await res.json()
  vm.value = data
  // defaults para edição
  liveSource.value.type = String(vm.value?.source_type || '')
  liveSource.value.folder_path = vm.value?.folder_path || ''
  liveSource.value.camera_id = vm.value?.camera_id ?? null
  liveSource.value.rtsp_url = vm.value?.rtsp_url || ''
  liveSource.value.fps = Number(vm.value?.fps) || null
  liveResolutionWidth.value = Number(vm.value?.resolution_width) || null
  liveResolutionHeight.value = Number(vm.value?.resolution_height) || null
  liveTrigger.value.type = String(vm.value?.trigger_type || '')
  liveTrigger.value.interval_ms = vm.value?.trigger_interval_ms || null
}

function connectWebSocket() {
  if (!vm.value) return
  try {
    let host = ''
    if (vm.value.ip_address && vm.value.port) {
      host = `${vm.value.ip_address}:${vm.value.port}`
    } else if (vm.value.django_url) {
      try { const u = new URL(vm.value.django_url); host = u.host } catch {}
    }
    if (!host) {
      wsStatus.value = 'Sem endpoint de WebSocket disponível'
      return
    }
    const httpProtocol = location.protocol === 'https:' ? 'https' : 'http'
    const sioUrl = `${httpProtocol}://${host}`
    wsStatus.value = 'Conectando...'
    sio = io(sioUrl, { transports: ['websocket', 'polling'] })
    sio.on('connect', () => { wsStatus.value = 'Conectado' })
    sio.on('disconnect', () => { wsStatus.value = 'Desconectado' })
    sio.on('connected', () => {})
    sio.on('test_result', (data) => {
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
      if (Array.isArray(data?.tools)) {
        liveToolDefs.value = data.tools
        // Se ainda não aplicamos a configuração da VM na edição online, faça agora
        if (!vmConfigApplied.value && Array.isArray(data.tools) && data.tools.length > 0) {
          try {
            toolsItems.value = data.tools.map((t, i) => ({
              order_index: Number(t.order_index ?? i),
              name: t.name,
              type: String(t.type || '').toLowerCase(),
              ROI: t.ROI && (t.ROI.shape || t.ROI.rect || t.ROI.circle || t.ROI.ellipse)
                ? t.ROI
                : { shape: 'rect', rect: normalizeROI(t.ROI) },
              inspec_pass_fail: !!t.inspec_pass_fail,
              method: t.method,
              normalize: t.normalize,
              ksize: t.ksize,
              sigma: t.sigma,
              mode: t.mode,
              th_min: t.th_min,
              th_max: t.th_max,
              kernel: t.kernel,
              open: t.open,
              close: t.close,
              shape: t.shape,
              area_min: t.area_min,
              area_max: t.area_max,
              total_area_test: t.total_area_test,
              blob_count_test: t.blob_count_test,
              test_total_area_min: t.test_total_area_min,
              test_total_area_max: t.test_total_area_max,
              test_blob_count_min: t.test_blob_count_min,
              test_blob_count_max: t.test_blob_count_max,
              contour_chain: t.contour_chain,
              approx_epsilon_ratio: t.approx_epsilon_ratio,
              polygon_max_points: t.polygon_max_points,
              operation: t.operation,
              reference_tool_id: t.reference_tool_id,
              custom_formula: t.custom_formula
            }))
            vmConfigApplied.value = true
          } catch {}
        }
      }
      metrics.value = {
        aprovados: data?.aprovados,
        reprovados: data?.reprovados,
        time: data?.time,
        frame: data?.frame
      }
    })
  } catch {
    wsStatus.value = 'Falha ao conectar'
  }
}

// Tools da inspeção selecionada (estado editável local)
const toolsItems = ref([])
watch(selectedInspectionId, async (inspId) => {
  toolsItems.value = []
  // Se já recebemos a configuração da VM nesta sessão, não sobrescrever com memória do backend
  if (vmConfigApplied.value) return
  if (!inspId) return
  try {
    const res = await apiFetch(`/api/inspections/${inspId}`)
    const data = await res.json()
    const list = Array.isArray(data?.tools) ? data.tools : []
    toolsItems.value = list.map((t, i) => ({
      order_index: Number(t.order_index ?? i),
      name: t.name,
      type: String(t.type || '').toLowerCase(),
      // Preserva ROI com shape quando existir; fallback para retângulo simples
      ROI: t.ROI && (t.ROI.shape || t.ROI.rect || t.ROI.circle || t.ROI.ellipse)
        ? t.ROI
        : { shape: 'rect', rect: normalizeROI(t.ROI) },
      inspec_pass_fail: !!t.inspec_pass_fail,
      method: t.method,
      normalize: t.normalize,
      ksize: t.ksize,
      sigma: t.sigma,
      mode: t.mode,
      th_min: t.th_min,
      th_max: t.th_max,
      kernel: t.kernel,
      open: t.open,
      close: t.close,
      shape: t.shape,
      area_min: t.area_min,
      area_max: t.area_max,
      total_area_test: t.total_area_test,
      blob_count_test: t.blob_count_test,
      test_total_area_min: t.test_total_area_min,
      test_total_area_max: t.test_total_area_max,
      test_blob_count_min: t.test_blob_count_min,
      test_blob_count_max: t.test_blob_count_max,
      contour_chain: t.contour_chain,
      approx_epsilon_ratio: t.approx_epsilon_ratio,
      polygon_max_points: t.polygon_max_points,
      operation: t.operation,
      reference_tool_id: t.reference_tool_id,
      custom_formula: t.custom_formula
    }))
  } catch {
    toolsItems.value = []
  }
})

function normalizeROI(r) {
  const x = Number(r?.rect?.x ?? r?.x ?? 0)
  const y = Number(r?.rect?.y ?? r?.y ?? 0)
  const w = Number(r?.rect?.w ?? r?.w ?? 0)
  const h = Number(r?.rect?.h ?? r?.h ?? 0)
  return { x, y, w, h }
}

function normalizeROIForSave(roi) {
  if (!roi || typeof roi !== 'object') return {}
  const out = { shape: roi.shape || undefined }
  if (roi.shape === 'rect' || (!roi.shape && 'x' in roi && 'y' in roi && 'w' in roi && 'h' in roi)) {
    const r = roi.rect || roi
    out.shape = 'rect'
    out.rect = { x: Number(r.x)||0, y: Number(r.y)||0, w: Number(r.w)||0, h: Number(r.h)||0 }
  } else if (roi.shape === 'circle' && roi.circle) {
    out.shape = 'circle'
    out.circle = { cx: Number(roi.circle.cx)||0, cy: Number(roi.circle.cy)||0, r: Number(roi.circle.r)||0 }
  } else if (roi.shape === 'ellipse' && roi.ellipse) {
    out.shape = 'ellipse'
    out.ellipse = { cx: Number(roi.ellipse.cx)||0, cy: Number(roi.ellipse.cy)||0, rx: Number(roi.ellipse.rx)||0, ry: Number(roi.ellipse.ry)||0, angle: Number(roi.ellipse.angle)||0 }
  }
  return out
}

let applyTimer = null
function scheduleApplyToVM() {
  if (applyTimer) window.clearTimeout(applyTimer)
  applyTimer = window.setTimeout(() => { applyToVM() }, 400)
}

function onTriggerTypeChange() {
  // Em modo 'trigger', interval não se aplica; zera para evitar confusão
  if (String(liveTrigger.value.type || '').toLowerCase() === 'trigger') {
    liveTrigger.value.interval_ms = null
  }
  scheduleApplyToVM()
}

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
    // Atualizar VM após ações que modificam estado
    if (action === 'start' || action === 'stop' || action === 'restart') {
      await loadVM()
    }
  } catch (e) {
    liveError.value = e?.message || 'Erro ao executar comando'
  } finally {
    vmActionLoading.value = false
  }
}

function applyFolderPath() {
  applyToVM()
}

async function applyToVM() {
  try {
    if (!selectedInspectionId.value) return
    applyLoading.value = true
    liveError.value = ''
    const srcType = String(liveSource.value?.type || '').toLowerCase()
    const source_config = {
      type: liveSource.value?.type || undefined,
      folder_path: srcType === 'pasta' ? (liveSource.value?.folder_path || undefined) : undefined,
      camera_id: srcType === 'camera' ? (liveSource.value?.camera_id ?? undefined) : undefined,
      rtsp_url: srcType === 'rtsp' ? (liveSource.value?.rtsp_url || undefined) : undefined,
      fps: Number(liveSource.value?.fps) || undefined,
      resolution: [Number(liveResolutionWidth.value)||undefined, Number(liveResolutionHeight.value)||undefined]
    }
    // Trigger: remover interval_ms quando for 'trigger'
    const trigType = String(liveTrigger.value?.type || '').toLowerCase() || undefined
    const trigger_config = {
      type: trigType,
      interval_ms: (trigType === 'continuous') ? (Number(liveTrigger.value?.interval_ms) || undefined) : undefined
    }
    const payload = {}
    if (
      source_config.type || source_config.folder_path || source_config.camera_id || source_config.rtsp_url || source_config.fps ||
      (Array.isArray(source_config.resolution) && (source_config.resolution[0] || source_config.resolution[1]))
    ) {
      payload.source_config = source_config
    }
    if (trigger_config.type || trigger_config.interval_ms) {
      payload.trigger_config = trigger_config
    }
    if (Array.isArray(toolsItems.value) && toolsItems.value.length > 0) {
      payload.tools = toolsItems.value.map(t => ({
        order_index: Number(t.order_index ?? 0),
        name: t.name,
        type: t.type,
        ROI: normalizeROIForSave(t.ROI),
        inspec_pass_fail: !!t.inspec_pass_fail,
        method: t.method,
        normalize: t.normalize,
        ksize: t.ksize,
        sigma: t.sigma,
        mode: t.mode,
        th_min: t.th_min,
        th_max: t.th_max,
        kernel: t.kernel,
        open: t.open,
        close: t.close,
        shape: t.shape,
        area_min: t.area_min,
        area_max: t.area_max,
        total_area_test: t.total_area_test,
        blob_count_test: t.blob_count_test,
        test_total_area_min: t.test_total_area_min,
        test_total_area_max: t.test_total_area_max,
        test_blob_count_min: t.test_blob_count_min,
        test_blob_count_max: t.test_blob_count_max,
        contour_chain: t.contour_chain,
        approx_epsilon_ratio: t.approx_epsilon_ratio,
        polygon_max_points: t.polygon_max_points,
        operation: t.operation,
        reference_tool_id: t.reference_tool_id,
        custom_formula: t.custom_formula
      }))
    }
    const res = await apiFetch(`/api/inspections/${selectedInspectionId.value}/update_vm`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      okStatuses: [200]
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({ erro: 'Falha ao aplicar configuração' }))
      throw new Error(err?.erro || 'Falha ao aplicar configuração')
    }
  } catch (e) {
    liveError.value = e?.message || 'Falha ao aplicar configuração'
  } finally {
    applyLoading.value = false
  }
}

// Handlers de eventos vindos do AoVivoImg
function onSelectTool(payload) {
  // apenas referência; edição é tratada pelos outros eventos
}

function onUpdateToolRoi({ index, roi, name }) {
  const t = toolsItems.value.find((it, i) => (i === index) || (name && it.name === name))
  if (!t) return
  // Permite receber ROI com shape (rect/circle/ellipse) ou bounding box
  if (roi && typeof roi === 'object' && (roi.shape || roi.rect || roi.circle || roi.ellipse)) {
    t.ROI = { ...roi }
  } else {
    t.ROI = {
      shape: 'rect',
      rect: { x: Number(roi?.x || 0), y: Number(roi?.y || 0), w: Number(roi?.w || 0), h: Number(roi?.h || 0) }
    }
  }
  scheduleApplyToVM()
}

function onUpdateToolParam({ index, key, value, name }) {
  // Reordenar via modal (ordem por índices)
  if (key === 'INSPECTION_REORDER' && value && Array.isArray(value.orderIndexes)) {
    const order = value.orderIndexes
    const plan = Array.isArray(value.composePlan) ? value.composePlan : []
    const dels = Array.isArray(value.deleteIndexes) ? value.deleteIndexes.slice().sort((a,b)=>b-a) : []

    // pool inicial = lista atual após exclusões
    let pool = toolsItems.value.slice()
    for (const di of dels) {
      if (di >= 0 && di < pool.length) pool.splice(di, 1)
    }

    // construir sequência seq a partir do composePlan: orig pega de pool, dup copia de pool
    const seq = []
    const makeCopy = (src, step) => {
      const c = JSON.parse(JSON.stringify(src))
      c.name = step?.name || `${src.name}_copy`
      return c
    }
    for (const step of plan) {
      if (!step || typeof step.index !== 'number') continue
      const src = pool[step.index]
      if (!src) continue
      seq.push(step.kind === 'dup' ? makeCopy(src, step) : src)
    }

    // order refere-se às posições em seq
    const newArr = order.map(i => seq[i]).filter(Boolean).map((t, i) => ({ ...t, order_index: i }))
    if (newArr.length === order.length) {
      toolsItems.value = newArr
      applyToVM()
    }
    return
  }
  // Adição de nova tool via AoVivoImg
  if (key === 'ADD_TOOL' && value && typeof value === 'object') {
    const i = Array.isArray(toolsItems.value) ? toolsItems.value.length : 0
    const nt = {
      order_index: Number(value.order_index ?? i),
      name: value.name || `tool_${i+1}`,
      type: String(value.type || '').toLowerCase(),
      ROI: normalizeROIForSave(value.ROI || { shape: 'rect', rect: { x: 0, y: 0, w: 100, h: 100 } }),
      inspec_pass_fail: !!value.inspec_pass_fail,
      method: value.method,
      normalize: value.normalize,
      ksize: value.ksize,
      sigma: value.sigma,
      mode: value.mode,
      th_min: value.th_min,
      th_max: value.th_max,
      kernel: value.kernel,
      open: value.open,
      close: value.close,
      shape: value.shape,
      area_min: value.area_min,
      area_max: value.area_max,
      total_area_test: value.total_area_test,
      blob_count_test: value.blob_count_test,
      test_total_area_min: value.test_total_area_min,
      test_total_area_max: value.test_total_area_max,
      test_blob_count_min: value.test_blob_count_min,
      test_blob_count_max: value.test_blob_count_max,
      contour_chain: value.contour_chain,
      approx_epsilon_ratio: value.approx_epsilon_ratio,
      polygon_max_points: value.polygon_max_points,
      operation: value.operation,
      reference_tool_id: value.reference_tool_id,
      custom_formula: value.custom_formula
    }
    toolsItems.value = [...toolsItems.value, nt]
    applyToVM()
    return
  }
  const t = toolsItems.value.find((it, i) => (i === index) || (name && it.name === name))
  if (!t) return
  if (key === 'name') {
    let nv = String(value || '').trim()
    // normalização igual ao painel: remove acentos e caracteres inválidos
    nv = nv
      .normalize('NFD').replace(/\p{Diacritic}+/gu, '')
      .replace(/\s+/g, '_')
      .replace(/[^a-zA-Z0-9_]/g, '_')
      .replace(/_+/g, '_')
      .replace(/^_+|_+$/g, '')
    if (!nv) return
    const already = toolsItems.value.some((it, i) => i !== index && String(it.name) === nv)
    if (already) return
    t.name = nv
    applyToVM()
    return
  }
  t[key] = value
  scheduleApplyToVM()
}

function onUpdateInspectionConfig(full) {
  if (!full || !Array.isArray(full.tools)) return
  toolsItems.value = full.tools.map((t, i) => ({
    order_index: Number(t.order_index ?? i),
    name: t.name,
    type: String(t.type || '').toLowerCase(),
    ROI: t.ROI,
    inspec_pass_fail: !!t.inspec_pass_fail,
    method: t.method,
    normalize: t.normalize,
    ksize: t.ksize,
    sigma: t.sigma,
    mode: t.mode,
    th_min: t.th_min,
    th_max: t.th_max,
    kernel: t.kernel,
    open: t.open,
    close: t.close,
    shape: t.shape,
    area_min: t.area_min,
    area_max: t.area_max,
    total_area_test: t.total_area_test,
    blob_count_test: t.blob_count_test,
    test_total_area_min: t.test_total_area_min,
    test_total_area_max: t.test_total_area_max,
    test_blob_count_min: t.test_blob_count_min,
    test_blob_count_max: t.test_blob_count_max,
    contour_chain: t.contour_chain,
    approx_epsilon_ratio: t.approx_epsilon_ratio,
    polygon_max_points: t.polygon_max_points,
    operation: t.operation,
    reference_tool_id: t.reference_tool_id,
    custom_formula: t.custom_formula
  }))
  scheduleApplyToVM()
}

// Removido: update-inspection-config

onMounted(loadInitial)
onBeforeUnmount(() => { try { if (sio) sio.disconnect() } catch {} sio = null })
</script>

<style scoped>
.bg-info {
  background: linear-gradient(135deg, #17a2b8 0%, #138496 100%) !important;
}
.opacity-75 { opacity: 0.75; }
.live-row .aovivoimg .frame-wrapper { min-height: 320px; }
</style>