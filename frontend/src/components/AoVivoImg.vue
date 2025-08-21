<template>
  <div class="aovivoimg">
    <div class="live-layout">
      <div class="left">
        <div class="frame-wrapper" :style="{ aspectRatio }">
          <template v-if="imageUrl">
            <img :src="imageUrl" :alt="alt" class="frame" :class="fitClass" />
            <div v-if="hasAnyOverlay" class="overlay">
              <div v-if="showOverlay" class="roi" :style="roiStyle"></div>
              <div
                v-for="(pt, i) in blobCentroidPoints"
                :key="`bc_${i}`"
                class="blob-cross"
                :style="{ left: pt.left, top: pt.top }"
              ></div>
              <div
                v-for="(box, i) in blobBoxes"
                :key="`bb_${i}`"
                class="blob-box"
                :style="box"
              ></div>
              <svg v-if="showBlobContours && hasContours" class="contour-svg" viewBox="0 0 100 100" preserveAspectRatio="none">
                <template v-for="(path, i) in contourPaths" :key="`cp_${i}`">
                  <path
                    :d="path"
                    fill="rgba(25, 135, 84, 0.25)"
                    stroke="rgba(25, 135, 84, 0.25)"
                    stroke-width="0.2"
                    vector-effect="non-scaling-stroke"
                    stroke-linejoin="round"
                    stroke-linecap="round"
                  />
                </template>
              </svg>
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
          <div class="tool-form">
            <div class="tabs">
              <button type="button" class="tab-btn" :class="{ active: activeTab === 'tests' }" @click="activeTab = 'tests'">Testes</button>
              <button type="button" class="tab-btn" :class="{ active: activeTab === 'params' }" @click="activeTab = 'params'">Parâmetros</button>
              <button type="button" class="tab-btn" :class="{ active: activeTab === 'analysis' }" @click="activeTab = 'analysis'">Análise</button>
            </div>
            <div class="tab-pane" v-show="activeTab === 'tests'">
              <FormKit type="form" :actions="false" disabled>
                <div class="form-section">
                  <div v-if="testsArray.length === 0" class="text-muted small">Sem testes.</div>
                  <div v-for="(test, i) in testsArray" :key="`test_${i}`" class="card-like">
                    <div class="test-card-header">
                      <div class="test-title">{{ testTitle(test) }}</div>
                      <span v-if="testPassValue(test) !== null" class="badge" :class="passBadgeClass(testPassValue(test))">
                        {{ testPassValue(test) ? 'Passou' : 'Falhou' }}
                      </span>
                    </div>
                    <div class="row g-2 mt-1">
                      <template v-for="([key, val], idx) in entriesWithoutMeta(test)" :key="`t_${i}_${key}_${idx}`">
                        <div class="col-12 col-md-6" v-if="isBoolean(val)">
                          <FormKit
                            type="checkbox"
                            :label="labelize(key)"
                            :model-value="val"
                            disabled
                          />
                        </div>
                        <div class="col-12 col-md-6" v-else-if="!isLargeObject(val)">
                          <FormKit
                            type="text"
                            :label="labelize(key)"
                            :model-value="formatValue(val)"
                            disabled
                          />
                        </div>
                        <div class="col-12" v-else>
                          <FormKit
                            type="textarea"
                            :label="labelize(key)"
                            :model-value="formatJson(val)"
                            :rows="4"
                            disabled
                          />
                        </div>
                      </template>
                      <div v-if="entriesWithoutMeta(test).length === 0 && !isBoolean(test?.value) && test?.value !== undefined" class="col-12">
                        <FormKit type="text" :label="labelize(testTitle(test))" :model-value="formatValue(test.value)" disabled />
                      </div>
                    </div>
                  </div>
                </div>
              </FormKit>
            </div>
            <div class="tab-pane" v-show="activeTab === 'params'">
              <FormKit type="form" :actions="false" disabled>
                <div class="form-section">
                  <div v-if="paramEntries.length === 0" class="text-muted small">Sem parâmetros.</div>
                  <template v-else>
                    <h6 class="section-subtitle">Configuração</h6>
                    <div class="row g-2 mb-2">
                      <template v-for="([key, val], idx) in groupedParams.primary" :key="`pp_${idx}_${key}`">
                        <div class="col-12 col-md-6" v-if="isBoolean(val)">
                          <FormKit type="checkbox" :label="labelize(key)" :model-value="val" disabled />
                        </div>
                        <div class="col-12 col-md-6" v-else-if="!isLargeObject(val)">
                          <FormKit type="text" :label="labelize(key)" :model-value="formatValue(val)" disabled />
                        </div>
                        <div class="col-12" v-else>
                          <FormKit type="textarea" :label="labelize(key)" :model-value="formatJson(val)" :rows="4" disabled />
                        </div>
                      </template>
                      <div v-if="groupedParams.primary.length === 0" class="text-muted small">—</div>
                    </div>

                    <h6 class="section-subtitle mt-2">Testes</h6>
                    <div class="row g-2 mb-2">
                      <template v-for="([key, val], idx) in groupedParams.testsEnabled" :key="`tp_${idx}_${key}`">
                        <div class="col-12 col-md-6">
                          <FormKit type="checkbox" :label="labelize(key)" :model-value="val" disabled />
                        </div>
                      </template>
                      <div v-if="groupedParams.testsEnabled.length === 0" class="text-muted small">—</div>
                    </div>

                    <h6 class="section-subtitle mt-2">Sem interação direta</h6>
                    <div class="row g-2">
                      <template v-for="([key, val], idx) in groupedParams.others" :key="`op_${idx}_${key}`">
                        <div class="col-12 col-md-6" v-if="isBoolean(val)">
                          <FormKit type="checkbox" :label="labelize(key)" :model-value="val" disabled />
                        </div>
                        <div class="col-12 col-md-6" v-else-if="!isLargeObject(val)">
                          <FormKit type="text" :label="labelize(key)" :model-value="formatValue(val)" disabled />
                        </div>
                        <div class="col-12" v-else>
                          <FormKit type="textarea" :label="labelize(key)" :model-value="formatJson(val)" :rows="4" disabled />
                        </div>
                      </template>
                      <div v-if="groupedParams.others.length === 0" class="text-muted small">—</div>
                    </div>
                  </template>
                </div>
              </FormKit>
            </div>
          </div>
          <div class="tab-pane" v-show="activeTab === 'analysis'">
            <div class="analysis-toolbar mb-2">
              <button type="button" class="toggle-btn" :class="{ active: showBlobCentroids }" @click="toggleBlobCentroids">Blobs: centróides</button>
              <button type="button" class="toggle-btn" :class="{ active: showBlobBoxes }" @click="toggleBlobBoxes">Blobs: áreas</button>
              <button type="button" class="toggle-btn" :class="{ active: showBlobContours }" @click="toggleBlobContours">Blobs: contornos</button>
            </div>
            <FormKit type="form" :actions="false" disabled>
              <div class="form-section">
                <div v-if="analysisEntries.length === 0" class="text-muted small">Sem dados de análise.</div>
                <div class="row g-2" v-else>
                  <template v-for="([key, val], idx) in analysisEntries" :key="`an_${idx}_${key}`">
                    <div class="col-12 col-md-6" v-if="isBoolean(val)">
                      <FormKit type="checkbox" :label="labelize(key)" :model-value="val" disabled />
                    </div>
                    <div class="col-12 col-md-6" v-else-if="!isLargeObject(val)">
                      <FormKit type="text" :label="labelize(key)" :model-value="formatValue(val)" disabled />
                    </div>
                    <div class="col-12" v-else>
                      <FormKit type="textarea" :label="labelize(key)" :model-value="formatJson(val)" :rows="4" disabled />
                    </div>
                  </template>
                </div>
              </div>
            </FormKit>
          </div>
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
const hasAnyOverlay = computed(() => showOverlay.value || (blobCentroidPoints.value && blobCentroidPoints.value.length > 0) || (blobBoxes.value && blobBoxes.value.length > 0))

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
  if (selectedIndex.value === idx) {
    // Toggle off
    selectedIndex.value = -1
    selectedRoi.value = null
    emit('select', null)
  } else {
    selectedIndex.value = idx
    selectedRoi.value = roi || null
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

// Helpers para o formulário somente leitura
const activeTab = ref('tests')
const testsArray = computed(() => {
  const it = selectedItem.value
  if (!it || typeof it !== 'object') return []
  // Preferir estrutura padronizada 'test_results'
  const tr = it.test_results
  if (tr && typeof tr === 'object') {
    const entries = Object.entries(tr).filter(([k]) => k !== 'overall_pass')
    const mapped = entries.map(([name, obj]) => {
      if (obj && typeof obj === 'object') return { name, ...obj }
      return { name, value: obj }
    })
    if (mapped.length === 0 && 'overall_pass' in tr) {
      return [{ name: 'Resultado Geral', value: tr.overall_pass }]
    }
    return mapped
  }
  // Fallbacks antigos
  const arr = []
  if (Array.isArray(it.tests)) arr.push(...it.tests)
  if (it.test && typeof it.test === 'object') arr.push(it.test)
  return arr.filter(t => t && typeof t === 'object')
})

const selectedDef = computed(() => {
  const it = selectedItem.value
  if (!it) return null
  return findToolDefForItem(it)
})

const paramEntries = computed(() => {
  const def = selectedDef.value
  const makeEntries = (obj) => {
    if (!obj || typeof obj !== 'object') return []
    const { id, name, type, ROI, roi, rect, bbox, /* inspec_pass_fail, */ reference_tool_id, tool_id, tool_name, tool_type, status, image_modified, pass_fail, processing_time_ms, error, blobs, blob_count, total_area, roi_area, test_results, ...rest } = obj
    // Remover campos de ROI explicitamente (não exibir)
    delete rest.ROI
    delete rest.roi
    delete rest.rect
    delete rest.bbox
    return Object.entries(rest)
  }
  const fromDef = makeEntries(def)
  if (fromDef.length) return fromDef
  // Fallback: tentar extrair do próprio item selecionado (caso este seja o config)
  return makeEntries(selectedItem.value)
})

// Agrupar parâmetros em categorias: configuração primária, testes e outros
const groupedParams = computed(() => {
  const entries = paramEntries.value
  const primary = []
  const tests = []
  const others = []

  const primaryKeys = new Set(['type', 'name', 'method', 'normalize', 'th_min', 'th_max', 'area_min', 'area_max', 'reference_tool_id', 'pass_fail'])
  const testKeyPattern = /^(test_|.*_test$|.*_min$|.*_max$)/i

  for (const [key, val] of entries) {
    if (primaryKeys.has(key)) {
      primary.push([key, val])
    } else if (key === 'inspec_pass_fail' || testKeyPattern.test(key)) {
      tests.push([key, val])
    } else {
      others.push([key, val])
    }
  }

  // Apenas flags booleanas de teste (habilitados), excluindo *_min, *_max e valores não booleanos
  const testsEnabled = tests.filter(([key, val]) => {
    if (/_min$|_max$/i.test(key)) return false
    return typeof val === 'boolean'
  })

  return { primary, tests, others, testsEnabled }
})

// Dados de análise: separar campos típicos de resultado da tool do item selecionado
const analysisEntries = computed(() => {
  const it = selectedItem.value
  if (!it || typeof it !== 'object') return []
  const {
    tool_id, tool_name, tool_type, status, image_modified, processing_time_ms,
    pass_fail, error, ROI, roi, rect, bbox, test_results, tests, test,
    // campos comumente volumosos
    blobs, blob_count, total_area, roi_area,
    ...rest
  } = it

  // Manter alguns campos de resultado úteis primeiro se existirem
  const preferredOrder = ['blob_count', 'total_area', 'roi_area']
  const result = []
  for (const key of preferredOrder) {
    if (key in it) result.push([key, it[key]])
  }
  // Adicionar o restante, exceto o que é metadata/config/testes
  for (const [k, v] of Object.entries(rest)) {
    result.push([k, v])
  }
  return result
})

// Toggle visual para centróides dos blobs
const showBlobCentroids = ref(false)
function toggleBlobCentroids() {
  showBlobCentroids.value = !showBlobCentroids.value
}

// Pontos de centróide dos blobs na imagem, em porcentagem relativa ao frame completo
const blobCentroidPoints = computed(() => {
  if (!showBlobCentroids.value) return []
  const it = selectedItem.value
  if (!it || typeof it !== 'object') return []
  // blobs podem estar em `blobs` (cada item contém centroid [x,y])
  const blobs = Array.isArray(it.blobs) ? it.blobs : []
  if (!blobs.length || baseWidth.value <= 0 || baseHeight.value <= 0) return []
  // Converter coordenadas do ROI para coordenadas globais se ROI estiver presente
  const roi = extractRoi(it) || selectedRoi.value
  const roiX = roi?.x || 0
  const roiY = roi?.y || 0
  return blobs
    .map(b => {
      const c = Array.isArray(b.centroid) ? b.centroid : null
      if (!c || c.length !== 2) return null
      const absX = roiX + Number(c[0] || 0)
      const absY = roiY + Number(c[1] || 0)
      if (!isFinite(absX) || !isFinite(absY)) return null
      const left = (absX / baseWidth.value) * 100
      const top = (absY / baseHeight.value) * 100
      return { left: `${left}%`, top: `${top}%` }
    })
    .filter(Boolean)
})

// Toggle áreas (bounding boxes) dos blobs
const showBlobBoxes = ref(false)
function toggleBlobBoxes() {
  showBlobBoxes.value = !showBlobBoxes.value
}

const blobBoxes = computed(() => {
  if (!showBlobBoxes.value) return []
  const it = selectedItem.value
  if (!it || typeof it !== 'object') return []
  const blobs = Array.isArray(it.blobs) ? it.blobs : []
  if (!blobs.length || baseWidth.value <= 0 || baseHeight.value <= 0) return []
  const roi = extractRoi(it) || selectedRoi.value
  const roiX = roi?.x || 0
  const roiY = roi?.y || 0
  return blobs
    .map(b => {
      const bb = Array.isArray(b.bounding_box) ? b.bounding_box : null
      if (!bb || bb.length !== 4) return null
      const [x, y, w, h] = bb.map(Number)
      if (![x, y, w, h].every(isFinite)) return null
      const absX = roiX + x
      const absY = roiY + y
      const left = (absX / baseWidth.value) * 100
      const top = (absY / baseHeight.value) * 100
      const width = (w / baseWidth.value) * 100
      const height = (h / baseHeight.value) * 100
      return {
        left: `${left}%`,
        top: `${top}%`,
        width: `${width}%`,
        height: `${height}%`
      }
    })
    .filter(Boolean)
})

// Contornos (polígonos) dos blobs renderizados como paths SVG
const showBlobContours = ref(false)
function toggleBlobContours() {
  showBlobContours.value = !showBlobContours.value
}

const hasContours = computed(() => {
  const it = selectedItem.value
  if (!it || typeof it !== 'object') return false
  return Array.isArray(it.blobs) && it.blobs.some(b => Array.isArray(b?.contour) && b.contour.length >= 3)
})

const contourPaths = computed(() => {
  if (!showBlobContours.value) return []
  const it = selectedItem.value
  if (!it || typeof it !== 'object') return []
  const blobs = Array.isArray(it.blobs) ? it.blobs : []
  if (!blobs.length || baseWidth.value <= 0 || baseHeight.value <= 0) return []
  const roi = extractRoi(it) || selectedRoi.value
  const roiX = roi?.x || 0
  const roiY = roi?.y || 0
  // Trabalhar com viewBox 0..100 -> normalizar para 0..100 sem '%' no path
  const toView = (x, y) => `${(x / baseWidth.value) * 100} ${(y / baseHeight.value) * 100}`
  const toPath = (pts) => {
    if (!pts || !pts.length) return ''
    const [x0, y0] = pts[0]
    let d = `M ${toView(roiX + x0, roiY + y0)}`
    for (let i = 1; i < pts.length; i++) {
      const [x, y] = pts[i]
      d += ` L ${toView(roiX + x, roiY + y)}`
    }
    d += ' Z'
    return d
  }
  return blobs
    .map(b => Array.isArray(b.contour) ? toPath(b.contour) : '')
    .filter(p => p)
})

function labelize(key) {
  if (!key) return ''
  return String(key)
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase())
}

function isBoolean(val) {
  return typeof val === 'boolean'
}

function isLargeObject(val) {
  if (!val || typeof val !== 'object') return false
  // Considera objeto grande se tiver arrays/objetos aninhados ou muitas chaves
  const keys = Object.keys(val)
  if (keys.length > 6) return true
  return keys.some(k => val[k] && typeof val[k] === 'object')
}

function formatValue(val) {
  if (val == null) return '—'
  if (typeof val === 'boolean') return val ? 'Sim' : 'Não'
  if (typeof val === 'number') return String(val)
  if (typeof val === 'string') return val
  return formatJson(val)
}

// Organização dos cards de teste
function testTitle(test) {
  if (!test || typeof test !== 'object') return 'Teste'
  if (typeof test.name === 'string') return labelize(test.name)
  // Tentar inferir título por convenções conhecidas
  const known = Object.keys(test).find(k => /^(total_area_test|blob_count_test|threshold_test)$/i.test(k))
  return known ? labelize(known) : 'Teste'
}

function testPassValue(test) {
  if (!test || typeof test !== 'object') return null
  if (typeof test.passed === 'boolean') return test.passed
  if (typeof test.ok === 'boolean') return test.ok
  if (typeof test.pass_fail === 'boolean') return test.pass_fail
  return null
}

function passBadgeClass(passed) {
  return passed ? 'bg-success text-white' : 'bg-danger text-white'
}

function entriesWithoutMeta(test) {
  if (!test || typeof test !== 'object') return []
  const { name, passed, ok, pass_fail, overall_pass, ...rest } = test
  return Object.entries(rest)
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

.blob-cross {
  position: absolute;
  width: 0;
  height: 0;
}
.blob-cross::before,
.blob-cross::after {
  content: '';
  position: absolute;
  background: rgba(25, 135, 84, 0.9); /* verde bootstrap 500 com opacidade */
}
.blob-cross::before {
  width: 12px;
  height: 2px;
  transform: translate(-6px, -1px);
}
.blob-cross::after {
  width: 2px;
  height: 12px;
  transform: translate(-1px, -6px);
}

.blob-box {
  position: absolute;
  border: 2px solid rgba(25, 135, 84, 0.6);
  box-shadow: 0 0 0 1px rgba(25, 135, 84, 0.2);
  border-radius: 2px;
}

.contour-svg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
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

.tool-details .tool-form {
  border: 1px solid #e9ecef;
  border-top: 0;
  border-radius: 0 0 10px 10px;
  background: #fff;
  padding: 12px;
}

.tabs {
  display: flex;
  gap: 6px;
  margin-bottom: 10px;
}

.tab-btn {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  padding: 6px 10px;
  cursor: pointer;
  font-weight: 600;
}

.tab-btn.active {
  background: #e7f1ff;
  border-color: #cfe2ff;
  color: #0d6efd;
}

.tab-pane {
  border-top: 1px dashed #e9ecef;
  padding-top: 10px;
}

.form-section .section-title {
  font-weight: 600;
  margin-bottom: 8px;
}

.card-like {
  border: 1px solid #f1f3f5;
  border-radius: 8px;
  padding: 10px;
  background: #f8f9fa;
  margin-bottom: 8px;
}

.section-subtitle {
  font-weight: 600;
  color: #495057;
}

.test-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.test-title {
  font-weight: 600;
}

.analysis-toolbar .toggle-btn {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  padding: 6px 10px;
  cursor: pointer;
  font-weight: 600;
}
.analysis-toolbar .toggle-btn.active {
  background: #e7f1ff;
  border-color: #cfe2ff;
  color: #0d6efd;
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


