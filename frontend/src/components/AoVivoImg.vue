<template>
  <div class="aovivoimg">
    <div class="live-layout">
      <div class="left">
        <div class="frame-wrapper" :style="{ aspectRatio }">
          <template v-if="imageUrl">
            <img :src="imageUrl" :alt="alt" class="frame" :class="fitClass" />
            <div v-if="showOverlay" class="overlay">
              <div class="roi" :style="roiStyle"></div>
            </div>
          </template>
          <div v-else class="placeholder">
            <slot>
              <span class="text-muted">Sem imagem ao vivo</span>
            </slot>
          </div>
        </div>
      </div>
      <div class="right">
        <div class="overall-status">
          <span class="badge" :class="statusBadgeClass">
            <Icon :name="statusIconName" size="1rem" class="me-1" />
            {{ statusText }}
          </span>
        </div>
        <div class="timeline">
          <div
            v-for="(dot, idx) in timelineDisplay"
            :key="`tl_${idx}`"
            class="timeline-dot"
            :class="{
              'tl-pass': dot === true,
              'tl-fail': dot === false,
              'tl-unknown': dot === null
            }"
          ></div>
        </div>
        <div class="metrics-panel">
          <div class="metrics-header">Métricas</div>
          <div class="metrics-grid">
            <div class="metric"><div class="label">Aprovados</div><div class="value">{{ metrics?.aprovados ?? '—' }}</div></div>
            <div class="metric"><div class="label">Reprovados</div><div class="value">{{ metrics?.reprovados ?? '—' }}</div></div>
            <div class="metric"><div class="label">Tempo</div><div class="value">{{ metrics?.time ?? '—' }}</div></div>
            <div class="metric"><div class="label">Frame</div><div class="value">{{ metrics?.frame ?? '—' }}</div></div>
          </div>
        </div>
        <div class="tool-details mt-3" v-if="selectedItem">
          <div class="tools-header">Configuração/Resultados da Tool</div>
          <pre class="tool-json">{{ formatJson(selectedItem) }}</pre>
        </div>
      </div>
    </div>
    <div v-if="displayItems.length" class="tools-panel mt-3">
      <div class="tools-header">Ciclo de Inspeção</div>
      <div class="tools-grid">
        <div
          v-for="(item, idx) in displayItems"
          :key="itemKey(item, idx)"
          class="tool-card"
          :title="cardTitle(item)"
          @click="handleItemClick(item, idx)"
          :class="cardClass(item, idx)"
        >
          <div class="status-dot" :class="statusClass(item)"></div>
          <div class="tool-name">{{ cardName(item) }}</div>
          <div class="tool-type">{{ cardType(item) }}</div>
          <div class="tool-meta" v-if="item?.processing_time_ms !== undefined">{{ item.processing_time_ms }} ms</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onBeforeUnmount, computed } from 'vue'
import Icon from '@/components/Icon.vue'

const props = defineProps({
  binary: {
    type: [ArrayBuffer, Uint8Array, Blob, String],
    default: null
  },
  tools: {
    type: Array,
    default: () => []
  },
  toolDefs: {
    type: Array,
    default: () => []
  },
  metrics: {
    type: Object,
    default: () => ({ aprovados: 0, reprovados: 0, time: '', frame: 0 })
  },
  results: {
    type: Array,
    default: () => []
  },
  resolution: {
    type: Array, // [width, height]
    default: () => []
  },
  mimeType: {
    type: String,
    default: 'image/jpeg'
  },
  alt: {
    type: String,
    default: 'Frame ao vivo'
  },
  fit: {
    type: String,
    default: 'contain' // contain | cover | fill | none | scale-down
  },
  ratio: {
    type: [String, Number],
    default: '16/9' // Ex.: '4/3', '1/1', 1.777...
  }
})

const emit = defineEmits(['select'])

const imageUrl = ref('')
let objectUrl = ''
const selectedIndex = ref(-1)
const selectedRoi = ref(null)
const hasAutoSelected = ref(false)

const aspectRatio = computed(() => {
  if (typeof props.ratio === 'number') return String(props.ratio)
  return props.ratio || '16/9'
})

const fitClass = computed(() => {
  return `fit-${props.fit}`
})

const displayItems = computed(() => {
  // Preferir results; se vazio, usar tools (compatibilidade)
  if (Array.isArray(props.results) && props.results.length) return props.results
  return Array.isArray(props.tools) ? props.tools : []
})

const baseWidth = computed(() => Array.isArray(props.resolution) ? Number(props.resolution[0]) || 0 : 0)
const baseHeight = computed(() => Array.isArray(props.resolution) ? Number(props.resolution[1]) || 0 : 0)

const showOverlay = computed(() => !!(selectedRoi.value && baseWidth.value > 0 && baseHeight.value > 0 && imageUrl.value))

const roiStyle = computed(() => {
  if (!showOverlay.value) return {}
  const { x = 0, y = 0, w = 0, h = 0 } = selectedRoi.value || {}
  const left = (x / baseWidth.value) * 100
  const top = (y / baseHeight.value) * 100
  const width = (w / baseWidth.value) * 100
  const height = (h / baseHeight.value) * 100
  return {
    left: `${left}%`,
    top: `${top}%`,
    width: `${width}%`,
    height: `${height}%`
  }
})

function revokeObjectUrl() {
  if (objectUrl) {
    URL.revokeObjectURL(objectUrl)
    objectUrl = ''
  }
}

function setFromBlob(blob) {
  revokeObjectUrl()
  objectUrl = URL.createObjectURL(blob)
  imageUrl.value = objectUrl
}

function base64ToBlob(base64, mime) {
  try {
    const byteChars = atob(base64)
    const byteNumbers = new Array(byteChars.length)
    for (let i = 0; i < byteChars.length; i++) {
      byteNumbers[i] = byteChars.charCodeAt(i)
    }
    const byteArray = new Uint8Array(byteNumbers)
    return new Blob([byteArray], { type: mime })
  } catch {
    return null
  }
}

watch(() => props.binary, (val) => {
  if (!val) {
    imageUrl.value = ''
    revokeObjectUrl()
    return
  }

  if (val instanceof Blob) {
    setFromBlob(val)
    return
  }

  if (val instanceof ArrayBuffer) {
    setFromBlob(new Blob([val], { type: props.mimeType }))
    return
  }

  if (val instanceof Uint8Array) {
    setFromBlob(new Blob([val], { type: props.mimeType }))
    return
  }

  if (typeof val === 'string') {
    // Se já for data URL ou URL, usa diretamente
    if (val.startsWith('data:') || val.startsWith('http')) {
      imageUrl.value = val
      revokeObjectUrl()
      return
    }
    // Caso seja base64 cru
    const blob = base64ToBlob(val, props.mimeType)
    if (blob) {
      setFromBlob(blob)
    }
  }
}, { immediate: true })

onBeforeUnmount(() => {
  revokeObjectUrl()
})

function normalizeRoi(roiLike) {
  if (!roiLike || typeof roiLike !== 'object') return null
  // Aceita formatos: {x,y,w,h} ou {x,y,width,height}
  const x = Number(roiLike.x ?? roiLike.left)
  const y = Number(roiLike.y ?? roiLike.top)
  const w = Number(roiLike.w ?? roiLike.width)
  const h = Number(roiLike.h ?? roiLike.height)
  if ([x, y, w, h].some(v => !isFinite(v))) return null
  if (w <= 0 || h <= 0) return null
  return { x, y, w, h }
}

function itemKey(item, idx) {
  const base = String(item?.id ?? item?.name ?? item?.type ?? '')
  return base || `idx_${idx}`
}

function cardTitle(item) {
  return cardName(item) || cardType(item)
}

function cardName(item) {
  return item?.name || item?.tool_name || 'Sem nome'
}

function cardType(item) {
  return item?.type || item?.tool_type || '—'
}

function extractRoi(item) {
  if (!item || typeof item !== 'object') return null
  // Possíveis campos: ROI/roi/rect/bbox
  return normalizeRoi(item.ROI || item.roi || item.rect || item.bbox)
}

function findToolDefForItem(item) {
  if (!item || !Array.isArray(props.toolDefs)) return null
  const tid = item.tool_id ?? item.id
  const tname = item.tool_name ?? item.name
  // Tenta casar por id, depois por nome, por fim por tipo + ordem
  let def = null
  if (tid != null) def = props.toolDefs.find(t => t.id === tid)
  if (!def && tname) def = props.toolDefs.find(t => t.name === tname)
  if (!def && item?.tool_type) {
    const defsOfType = props.toolDefs.filter(t => t.type === item.tool_type)
    def = defsOfType[0] || null
  }
  return def || null
}

function extractPassFail(item) {
  // Retorna true/false/undefined
  if (typeof item?.pass_fail === 'boolean') return item.pass_fail
  // Procura dentro de campos 'test' ou 'tests'
  const candidates = []
  if (item?.test) candidates.push(item.test)
  if (Array.isArray(item?.tests)) candidates.push(...item.tests)
  for (const t of candidates) {
    if (t && typeof t === 'object') {
      if (typeof t.pass_fail === 'boolean') return t.pass_fail
      // variações
      if (typeof t.passed === 'boolean') return t.passed
      if (typeof t.ok === 'boolean') return t.ok
    }
  }
  return undefined
}

function handleItemClick(item, idx) {
  let roi = extractRoi(item)
  if (!roi) {
    const def = findToolDefForItem(item)
    roi = extractRoi(def)
  }
  if (!roi) return
  if (selectedIndex.value === idx) {
    // Toggle off
    selectedIndex.value = -1
    selectedRoi.value = null
    emit('select', null)
  } else {
    selectedIndex.value = idx
    selectedRoi.value = roi
    emit('select', {
      index: idx,
      item,
      roi,
      pass_fail: extractPassFail(item)
    })
  }
}

function isToolSelectedIdx(idx) {
  return selectedIndex.value === idx
}

// Auto-seleção da primeira ferramenta na primeira carga
watch([() => props.results, () => props.tools], ([resultsList, toolsList]) => {
  if (hasAutoSelected.value) return
  const src = (Array.isArray(resultsList) && resultsList.length) ? resultsList : toolsList
  if (Array.isArray(src) && src.length > 0) {
    const first = src[0]
    selectedIndex.value = 0
    selectedRoi.value = extractRoi(first)
    hasAutoSelected.value = true
  }
}, { immediate: true })

function cardClass(item, idx) {
  return { selected: isToolSelectedIdx(idx) }
}

function statusClass(item) {
  const pf = extractPassFail(item)
  if (pf === true) return 'status-pass'
  if (pf === false) return 'status-fail'
  return 'status-unknown'
}

const selectedItem = computed(() => {
  if (selectedIndex.value < 0) return null
  return displayItems.value[selectedIndex.value] || null
})

function formatJson(obj) {
  try { return JSON.stringify(obj, null, 2) } catch { return String(obj) }
}

// Status geral (aprovado/reprovado/indefinido)
const overallPass = computed(() => {
  const items = displayItems.value || []
  let anyFalse = false
  let anyTrue = false
  for (const it of items) {
    const pf = extractPassFail(it)
    if (pf === false) { anyFalse = true; break }
    if (pf === true) { anyTrue = true }
  }
  if (anyFalse) return false
  if (anyTrue) return true
  return null
})

const statusIconName = computed(() => {
  if (overallPass.value === true) return 'check-circle-fill'
  if (overallPass.value === false) return 'x-circle-fill'
  return 'dash-circle'
})

// Cores do ícone são controladas pelo badge

const statusText = computed(() => {
  if (overallPass.value === true) return 'Aprovado'
  if (overallPass.value === false) return 'Reprovado'
  return 'Indefinido'
})

// Mantido apenas badge para cor

const statusBadgeClass = computed(() => {
  if (overallPass.value === true) return 'bg-success text-white'
  if (overallPass.value === false) return 'bg-danger text-white'
  return 'bg-secondary text-white'
})

// Linha do tempo de resultados (memória temporária em runtime)
const timelineDots = ref([])
const maxTimeline = 60
const lastFrameSeen = ref(0)

watch(() => props.metrics?.frame, (frameVal) => {
  if (typeof frameVal !== 'number') return
  // Se frame reiniciou ou diminuiu (reload), limpa timeline
  if (frameVal <= lastFrameSeen.value) {
    timelineDots.value = []
  }
  lastFrameSeen.value = frameVal
  // Adiciona estado atual
  timelineDots.value.push(overallPass.value)
  if (timelineDots.value.length > maxTimeline) {
    timelineDots.value.splice(0, timelineDots.value.length - maxTimeline)
  }
})

// Exibição invertida (mais recente à esquerda) e preenchimento com cinza
const timelineDisplay = computed(() => {
  const arr = timelineDots.value.slice(-maxTimeline)
  const rev = arr.slice().reverse()
  const padCount = Math.max(0, maxTimeline - rev.length)
  return rev.concat(Array(padCount).fill(null))
})
</script>

<style scoped>
.aovivoimg {
  width: 100%;
}

.live-layout {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}

@media (min-width: 992px) {
  .live-layout {
    grid-template-columns: 2fr 1fr;
    align-items: start;
  }
}

.frame-wrapper {
  position: relative;
  width: 100%;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  overflow: hidden;
}

.frame {
  width: 100%;
  height: 100%;
  display: block;
}

.overlay {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.roi {
  position: absolute;
  border: 2px solid #0d6efd; /* azul bootstrap */
  box-shadow: 0 0 0 1px rgba(13,110,253,.2);
}

.fit-contain { object-fit: contain; }
.fit-cover { object-fit: cover; }
.fit-fill { object-fit: fill; }
.fit-none { object-fit: none; }
.fit-scale-down { object-fit: scale-down; }

.placeholder {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6c757d;
}

.tools-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 8px;
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

.overall-status {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.status-text {
  font-weight: 600;
}

.timeline {
  display: grid;
  grid-template-columns: repeat(60, 1fr);
  gap: 4px;
  margin-bottom: 12px;
}

.timeline-dot {
  width: 100%;
  height: 10px;
  border-radius: 2px;
  background: #adb5bd; /* unknown */
}

.timeline-dot.tl-pass { background: #198754; }
.timeline-dot.tl-fail { background: #dc3545; }
.timeline-dot.tl-unknown { background: #adb5bd; }

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

.tools-panel {
  border: 1px solid #e9ecef;
  border-radius: 10px;
  background: #fff;
}

.tools-header {
  font-weight: 600;
  padding: 10px 12px;
  border-bottom: 1px solid #e9ecef;
}

.tool-card {
  aspect-ratio: 1 / 1;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #fff;
  cursor: pointer;
  transition: border-color .15s ease, box-shadow .15s ease, transform .05s ease;
  position: relative;
}

.tool-name {
  font-weight: 600;
  font-size: 0.95rem;
}

.tool-type {
  color: #6c757d;
  font-size: 0.85rem;
}

.tool-card:hover {
  border-color: #cfe2ff;
  box-shadow: 0 2px 8px rgba(13,110,253,.1);
}

.tool-card.selected {
  border-color: #0d6efd;
  box-shadow: 0 0 0 2px rgba(13,110,253,.2);
}

.tool-meta {
  margin-top: 4px;
  font-size: 0.8rem;
  color: #6c757d;
}

.status-dot {
  position: absolute;
  top: 8px;
  left: 8px;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  box-shadow: 0 0 0 2px #fff;
}

.status-pass { background: #198754; }
.status-fail { background: #dc3545; }
.status-unknown { background: #adb5bd; }
</style>


