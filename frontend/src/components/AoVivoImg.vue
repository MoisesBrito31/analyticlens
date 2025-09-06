<template>
  <div class="aovivoimg">
    <div class="live-layout">
      <div class="left">
        <div class="frame-wrapper" :style="{ aspectRatio }">
          <template v-if="imageUrl">
            <img :src="imageUrl" :alt="alt" class="frame" :class="fitClass" />
            <div v-if="hasAnyOverlay" class="overlay">
              <RoiOverlay
                :view-box="svgViewBox"
                :show-rect-overlay="showRectOverlay"
                :effective-roi-rect="effectiveRoiRect"
                :show-circle-overlay="showCircleOverlay"
                :roi-circle="roiCircle"
                :show-ellipse-overlay="showEllipseOverlay"
                :roi-ellipse="roiEllipse"
                :show-blob-centroids="showBlobCentroids"
                :blob-centroid-points-px="blobCentroidPointsPx"
                :show-blob-boxes="showBlobBoxes"
                :blob-boxes-px="blobBoxesPx"
                :show-blob-contours="showBlobContours"
                :contour-paths="contourPaths"
                :has-contours="hasContours"
                :analysis-colors="analysisColors"
                :editable="isEditingEnabled"
                :roi-shape="selectedRoiShape"
                @roi-change="onRoiChange"
              />
            </div>
          </template>
          <div v-else class="placeholder">
            <slot>
              <span class="text-muted">Sem imagem ao vivo</span>
            </slot>
          </div>
        </div>
        <ToolCardsPanel
          v-if="displayItems.length"
          class="mt-3"
          :items="displayItems"
          :selected-index="selectedIndex"
          :read-only="props.readOnly"
          @select="onSelectCard"
          @add-tool="onAddTool"
          @reorder="onReorderExternal"
          @delete-tool="onDeleteTool"
        />
      </div>
      <div class="right">
        <div class="overall-status">
          <span class="badge" :class="statusBadgeClass">
            <Icon :name="statusIconName" size="1rem" class="me-1" />
            {{ statusText }}
          </span>
        </div>
        <TimelineDots :dots="timelineDisplay" :columns="60" />
        <div class="metrics-panel">
          <MetricsPanel :metrics="metrics" />
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
              <ToolParamsPanel
                :type="selectedToolType"
                :params="activeParams"
                :read-only="props.readOnly"
                :roi="selectedRoiShape"
                :all-names="displayItems.map(t => t?.name || t?.tool_name || '')"
                :current-name="selectedItem?.name || selectedItem?.tool_name || ''"
                @update="onParamsUpdate"
              />
            </div>
          </div>
          <div class="tab-pane" v-show="activeTab === 'analysis'">
            <div class="analysis-toolbar mb-2" v-if="selectedItem && (selectedItem.tool_type === 'blob' || selectedItem.type === 'blob')">
              <button type="button" class="toggle-btn" :class="{ active: showBlobCentroids }" @click="toggleBlobCentroids">Blobs: centróides</button>
              <button type="button" class="toggle-btn" :class="{ active: showBlobBoxes }" @click="toggleBlobBoxes">Blobs: áreas</button>
              <button type="button" class="toggle-btn" :class="{ active: showBlobContours }" @click="toggleBlobContours">Blobs: contornos</button>
            </div>
            <!-- Tabela de blobs: centroide e área -->
            <div v-if="selectedItem && (selectedItem.tool_type === 'blob' || selectedItem.type === 'blob')" class="mb-2">
              <h6 class="section-subtitle">Blobs</h6>
              <div v-if="blobAnalysisRows.length === 0" class="text-muted small">Sem blobs.</div>
              <div v-else class="card-like">
                <table class="blob-table">
                  <thead>
                    <tr>
                      <th style="width: 60px">#</th>
                      <th>Centroide (x, y)</th>
                      <th style="width: 140px">Área</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="row in blobAnalysisRows" :key="`br_${row.index}`">
                      <td>{{ row.index }}</td>
                      <td>{{ row.cx }}, {{ row.cy }}</td>
                      <td>{{ formatNumber(row.area) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
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
    
  </div>
</template>

<script setup>
import { ref, watch, onBeforeUnmount, computed } from 'vue'
import Icon from '@/components/Icon.vue'
import TimelineDots from '@/components/TimelineDots.vue'
import MetricsPanel from '@/components/MetricsPanel.vue'
import ToolParamsPanel from '@/components/ToolParamsPanel.vue'
import { useToolParams } from '@/composables/useToolParams'
import RoiOverlay from '@/components/RoiOverlay.vue'
import ToolCardsPanel from '@/components/ToolCardsPanel.vue'

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
  },
  readOnly: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['select', 'update-tool-param', 'update-inspection-config'])

const imageUrl = ref('')
let objectUrl = ''
const selectedIndex = ref(-1)
const selectedRoi = ref(null)
const selectedRoiShape = ref(null)
const hasAutoSelected = ref(false)
const isEditingEnabled = computed(() => !props.readOnly && !!selectedRoiShape.value)

// Debug JSONs
const lastSentJson = ref('')
const lastReceivedJson = ref('')


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

// Removido reorder otimista: a ordem deve refletir estritamente o JSON recebido

const baseWidth = computed(() => Array.isArray(props.resolution) ? Number(props.resolution[0]) || 0 : 0)
const baseHeight = computed(() => Array.isArray(props.resolution) ? Number(props.resolution[1]) || 0 : 0)

const svgViewBox = computed(() => `0 0 ${baseWidth.value || 100} ${baseHeight.value || 100}`)

const showRectOverlay = computed(() => {
  if (!(effectiveRoiRect.value && baseWidth.value > 0 && baseHeight.value > 0 && imageUrl.value)) return false
  const s = selectedRoiShape.value
  // Só exibe retângulo quando o shape é retângulo (ou legacy sem shape)
  if (!s || s.shape === 'rect') return true
  return false
})
const hasAnyOverlay = computed(() => showRectOverlay.value || showCircleOverlay.value || showEllipseOverlay.value || (blobCentroidPointsPx.value && blobCentroidPointsPx.value.length > 0) || (blobBoxesPx.value && blobBoxesPx.value.length > 0))

// Não usamos mais CSS percent para ROI; tudo em SVG coordenado pela resolução

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

// Atualiza JSON recebido (somente tools/results) sempre que props mudarem
watch([() => props.tools, () => props.results], () => {
  const recv = { tools: props.tools || [], results: props.results || [] }
  try { lastReceivedJson.value = JSON.stringify(recv, null, 2) } catch { lastReceivedJson.value = String(recv) }
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

function extractRoiShape(obj) {
  if (!obj || typeof obj !== 'object') return null
  const roi = obj.ROI || obj.roi
  if (!roi || typeof roi !== 'object') return null
  // Novo formato tipado
  if (typeof roi.shape === 'string') {
    const shape = roi.shape
    if (shape === 'rect') {
      const r = roi.rect || roi
      const rect = normalizeRoi(r)
      return rect ? { shape: 'rect', rect } : null
    }
    if (shape === 'circle' && roi.circle) {
      const cx = Number(roi.circle.cx), cy = Number(roi.circle.cy), r = Number(roi.circle.r)
      if ([cx, cy, r].every(isFinite) && r > 0) return { shape: 'circle', circle: { cx, cy, r } }
      return null
    }
    if (shape === 'ellipse' && roi.ellipse) {
      const cx = Number(roi.ellipse.cx), cy = Number(roi.ellipse.cy)
      const rx = Number(roi.ellipse.rx), ry = Number(roi.ellipse.ry)
      const angle = Number(roi.ellipse.angle || 0)
      if ([cx, cy, rx, ry].every(isFinite) && rx > 0 && ry > 0) return { shape: 'ellipse', ellipse: { cx, cy, rx, ry, angle } }
      return null
    }
  }
  // Legacy {x,y,w,h}
  const rect = normalizeRoi(roi)
  return rect ? { shape: 'rect', rect } : null
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
  if (!item) return null
  const byIdOrName = (arr) => {
    if (!Array.isArray(arr)) return null
    const tid = item.tool_id ?? item.id
    const tname = item.tool_name ?? item.name
    let def = null
    if (tid != null) def = arr.find(t => t.id === tid)
    if (!def && tname) def = arr.find(t => t.name === tname)
    if (!def && (item?.tool_type || item?.type)) {
      const ty = item.tool_type || item.type
      def = arr.find(t => t.type === ty) || null
    }
    return def || null
  }
  // Prioriza props.tools (definições carregadas), depois toolDefs
  return byIdOrName(props.tools) || byIdOrName(props.toolDefs)
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

// Constrói JSON completo da inspeção a partir dos itens atuais
function buildInspectionPayload(overrides = {}) {
  // Fonte na ordem atual
  const src = displayItems.value || []
  // Reordenar por ids se informado
  let toolsOrdered = src
  // Se uma lista já ordenada for fornecida, usa diretamente
  if (Array.isArray(overrides.toolsOrdered) && overrides.toolsOrdered.length) {
    toolsOrdered = overrides.toolsOrdered
  }
  if (Array.isArray(overrides.order) && overrides.order.length) {
    const idOf = (it) => it?.tool_id ?? it?.id
    const mapById = new Map(src.map(it => [idOf(it), it]))
    toolsOrdered = overrides.order.map(id => mapById.get(id)).filter(Boolean)
  }

  const getVal = (it, def, key, fallback) => {
    const v = it?.[key]
    if (v !== undefined) return v
    const dv = def?.[key]
    if (dv !== undefined) return dv
    return fallback
  }

  const pickCalibration = (obj, keys) => {
    const out = {}
    for (const k of keys) {
      if (obj[k] !== undefined) out[k] = obj[k]
    }
    return out
  }

  const resultTools = toolsOrdered.map((it, idx) => {
    const def = findToolDefForItem(it) || {}
    const id = getVal(it, def, 'id', idx)
    const name = getVal(it, def, 'name', getVal(it, def, 'tool_name', `tool_${id}`))
    const type = String(getVal(it, def, 'type', getVal(it, def, 'tool_type', ''))).toLowerCase()
    const base = { id, name, type, order_index: idx }
    // ROI
    if (overrides.applyRoiAtIndex === idx && overrides.roiValue) {
      base.ROI = overrides.roiValue
    } else {
      const shapeObj = extractRoiShape(it) || extractRoiShape(def)
      if (shapeObj) base.ROI = shapeObj
    }
    // Campos comuns
    base.inspec_pass_fail = !!getVal(it, def, 'inspec_pass_fail', false)
    base.reference_tool_id = getVal(it, def, 'reference_tool_id', null)

    // Params por tipo (enviar todos, com defaults onde fizer sentido)
    if (type === 'blob') {
      base.th_min = Number(getVal(it, def, 'th_min', 0))
      base.th_max = Number(getVal(it, def, 'th_max', 255))
      base.area_min = Number(getVal(it, def, 'area_min', 0))
      base.area_max = Number(getVal(it, def, 'area_max', 1e12))
      base.total_area_test = !!getVal(it, def, 'total_area_test', false)
      base.blob_count_test = !!getVal(it, def, 'blob_count_test', false)
      base.test_total_area_min = Number(getVal(it, def, 'test_total_area_min', 0))
      base.test_total_area_max = Number(getVal(it, def, 'test_total_area_max', 1e12))
      base.test_blob_count_min = Number(getVal(it, def, 'test_blob_count_min', 0))
      base.test_blob_count_max = Number(getVal(it, def, 'test_blob_count_max', 1000000))
      base.pre_blur = String(getVal(it, def, 'pre_blur', '')) || null
      base.pre_blur_ksize = Number(getVal(it, def, 'pre_blur_ksize', 3))
      base.pre_blur_sigma = Number(getVal(it, def, 'pre_blur_sigma', 0))
      base.morph_kernel = Number(getVal(it, def, 'morph_kernel', 3))
      base.morph_open = Number(getVal(it, def, 'morph_open', 0))
      base.morph_close = Number(getVal(it, def, 'morph_close', 0))
      base.use_range_threshold = !!getVal(it, def, 'use_range_threshold', false)
      base.use_otsu = !!getVal(it, def, 'use_otsu', false)
      base.contour_chain = String(getVal(it, def, 'contour_chain', 'SIMPLE')).toUpperCase()
      base.approx_epsilon_ratio = Number(getVal(it, def, 'approx_epsilon_ratio', 0))
      base.polygon_max_points = Number(getVal(it, def, 'polygon_max_points', 0))
    } else if (type === 'grayscale') {
      base.method = String(getVal(it, def, 'method', 'luminance'))
      base.normalize = !!getVal(it, def, 'normalize', false)
    } else if (type === 'blur') {
      base.method = String(getVal(it, def, 'method', 'gaussian'))
      base.ksize = Number(getVal(it, def, 'ksize', 3))
      base.sigma = Number(getVal(it, def, 'sigma', 0))
    } else if (type === 'threshold') {
      base.mode = String(getVal(it, def, 'mode', 'binary'))
      base.th_min = Number(getVal(it, def, 'th_min', 0))
      base.th_max = Number(getVal(it, def, 'th_max', 255))
    } else if (type === 'morphology') {
      base.kernel = Number(getVal(it, def, 'kernel', 3))
      base.open = Number(getVal(it, def, 'open', 0))
      base.close = Number(getVal(it, def, 'close', 0))
      base.shape = String(getVal(it, def, 'shape', 'ellipse'))
    } else if (type === 'math') {
      base.operation = String(getVal(it, def, 'operation', ''))
      base.reference_tool_id = getVal(it, def, 'reference_tool_id', null)
      base.custom_formula = String(getVal(it, def, 'custom_formula', ''))
    }
    return base
  })

  return { tools: resultTools }
}

function handleItemClick(item, idx) {
  let roi = extractRoi(item)
  let roiShape = extractRoiShape(item)
  if (!roi) {
    const def = findToolDefForItem(item)
    // Se o item já for uma definição (tem ROI shape), usa diretamente
    roi = extractRoi(def) || extractRoi(item)
    if (!roiShape) roiShape = extractRoiShape(def) || extractRoiShape(item)
  }
  if (selectedIndex.value === idx) {
    // Toggle off
    selectedIndex.value = -1
    selectedRoi.value = null
    selectedRoiShape.value = null
    emit('select', null)
  } else {
    selectedIndex.value = idx
    selectedRoi.value = roi || null
    selectedRoiShape.value = roiShape || (roi ? { shape: 'rect', rect: roi } : null)
    emit('select', {
      index: idx,
      item,
      roi,
      pass_fail: extractPassFail(item)
    })
  }
}

function onSelectCard(idx) {
  const item = displayItems.value[idx]
  if (!item) return
  handleItemClick(item, idx)
}

// Removido: handlers de reordenação

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
    const roi = extractRoi(first)
    const roiShape = extractRoiShape(first)
    selectedRoi.value = roi || null
    selectedRoiShape.value = roiShape || (roi ? { shape: 'rect', rect: roi } : null)
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

// Bounding box efetivo (para offsets dos blobs) baseado em ROI retângulo ou shape
const effectiveRoiRect = computed(() => {
  if (selectedRoi.value && typeof selectedRoi.value === 'object') return selectedRoi.value
  const s = selectedRoiShape.value
  if (!s || typeof s !== 'object') return null
  if (s.shape === 'rect' && s.rect) return s.rect
  if (s.shape === 'circle' && s.circle) {
    const { cx, cy, r } = s.circle
    return { x: cx - r, y: cy - r, w: 2 * r, h: 2 * r }
  }
  if (s.shape === 'ellipse' && s.ellipse) {
    const { cx, cy, rx, ry } = s.ellipse
    return { x: cx - rx, y: cy - ry, w: 2 * rx, h: 2 * ry }
    
  }
  return null
})

// ROI overlay shapes
const showCircleOverlay = computed(() => !!(selectedRoiShape.value && selectedRoiShape.value.shape === 'circle' && baseWidth.value > 0 && baseHeight.value > 0 && imageUrl.value))
const showEllipseOverlay = computed(() => !!(selectedRoiShape.value && selectedRoiShape.value.shape === 'ellipse' && baseWidth.value > 0 && baseHeight.value > 0 && imageUrl.value))

const roiCircle = computed(() => {
  if (!showCircleOverlay.value) return { cx: 0, cy: 0, r: 0 }
  const s = selectedRoiShape.value
  // Alguns resultados podem vir com bounding box apenas; se houver, usa-o para derivar cx,cy,r
  if (s.circle) {
    const { cx, cy, r } = s.circle
    return { cx, cy, r }
  }
  const r = effectiveRoiRect.value
  if (r) {
    const cx = r.x + r.w / 2
    const cy = r.y + r.h / 2
    const rad = Math.min(r.w, r.h) / 2
    return { cx, cy, r: rad }
  }
  return { cx: 0, cy: 0, r: 0 }
})

const roiEllipse = computed(() => {
  if (!showEllipseOverlay.value) return { cx: 0, cy: 0, rx: 0, ry: 0, angle: 0 }
  const { cx, cy, rx, ry, angle = 0 } = selectedRoiShape.value.ellipse
  return { cx, cy, rx, ry, angle }
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

// removido: paramEntries não utilizado após refatoração

// Removido groupedParams não utilizado
// Dados de análise: separar campos típicos de resultado da tool do item selecionado
const analysisEntries = computed(() => {
  const it = selectedItem.value
  if (!it || typeof it !== 'object') return []
  const exclude = new Set([
    'tool_id','tool_name','tool_type','status','image_modified','processing_time_ms',
    'pass_fail','error','ROI','roi','rect','bbox','test_results','tests','test','blobs'
  ])
  const preferredOrder = ['blob_count', 'total_area', 'roi_area']
  const added = new Set()
  const result = []
  for (const key of preferredOrder) {
    if (Object.prototype.hasOwnProperty.call(it, key)) {
      result.push([key, it[key]])
      added.add(key)
    }
  }
  for (const [k, v] of Object.entries(it)) {
    if (exclude.has(k) || added.has(k)) continue
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
const blobCentroidPointsPx = computed(() => {
  if (!showBlobCentroids.value) return []
  const it = selectedItem.value
  if (!it || typeof it !== 'object') return []
  const blobs = Array.isArray(it.blobs) ? it.blobs : []
  if (!blobs.length || baseWidth.value <= 0 || baseHeight.value <= 0) return []
  const roi = extractRoi(it) || effectiveRoiRect.value
  const roiX = roi?.x || 0
  const roiY = roi?.y || 0
  return blobs
    .map(b => {
      const c = Array.isArray(b.centroid) ? b.centroid : null
      if (!c || c.length !== 2) return null
      const absX = roiX + Number(c[0] || 0)
      const absY = roiY + Number(c[1] || 0)
      if (!isFinite(absX) || !isFinite(absY)) return null
      return { x: absX, y: absY }
    })
    .filter(Boolean)
})

// Toggle áreas (bounding boxes) dos blobs
const showBlobBoxes = ref(false)
function toggleBlobBoxes() {
  showBlobBoxes.value = !showBlobBoxes.value
}

const blobBoxesPx = computed(() => {
  if (!showBlobBoxes.value) return []
  const it = selectedItem.value
  if (!it || typeof it !== 'object') return []
  const blobs = Array.isArray(it.blobs) ? it.blobs : []
  if (!blobs.length || baseWidth.value <= 0 || baseHeight.value <= 0) return []
  const roi = extractRoi(it) || effectiveRoiRect.value
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
      return { x: absX, y: absY, w, h }
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
  const roi = extractRoi(it) || effectiveRoiRect.value
  const roiX = roi?.x || 0
  const roiY = roi?.y || 0
  // Usar coordenadas no espaço de pixels da imagem (viewBox = resolução real)
  const toView = (x, y) => `${x} ${y}`
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

// Linhas para tabela de análise de blobs
const blobAnalysisRows = computed(() => {
  const it = selectedItem.value
  if (!it || typeof it !== 'object') return []
  const blobs = Array.isArray(it.blobs) ? it.blobs : []
  return blobs.map((b, idx) => {
    const c = Array.isArray(b.centroid) ? b.centroid : [0, 0]
    const area = Number(b.area || 0)
    return {
      index: idx + 1,
      cx: Number(c[0] || 0),
      cy: Number(c[1] || 0),
      area
    }
  })
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

// Formatação numérica simples
function formatNumber(n) {
  const num = Number(n)
  if (!isFinite(num)) return '—'
  if (Math.abs(num) >= 1000) return String(Math.round(num))
  return num.toFixed(2)
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
  const rest = { ...test }
  delete rest.name
  delete rest.passed
  delete rest.ok
  delete rest.pass_fail
  delete rest.overall_pass
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

// Cores reativas para análise (verde se passou, vermelho se falhou)
const analysisColors = computed(() => {
  const it = selectedItem.value
  const pf = it ? (typeof it.pass_fail === 'boolean' ? it.pass_fail : undefined) : undefined
  const isFail = pf === false
  return {
    strokeStrong: isFail ? 'rgba(220, 53, 69, 0.95)' : 'rgba(25, 135, 84, 0.9)', // vermelho forte vs verde
    strokeMed: isFail ? 'rgba(220, 53, 69, 0.75)' : 'rgba(25, 135, 84, 0.6)',
    fillContour: isFail ? 'rgba(220, 53, 69, 0.25)' : 'rgba(25, 135, 84, 0.25)'
  }
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

// Removido handleParamChange não utilizado

const isBlobSelected = computed(() => {
  const it = selectedItem.value
  const t = String(it?.tool_type || it?.type || '').toLowerCase()
  return t === 'blob'
})

// opções de blob agora definidas no ToolParamsPanel

const blobParams = ref({
  inspec_pass_fail: false,
  th_min: 0,
  th_max: 255,
  area_min: 0,
  area_max: 1e12,
  total_area_test: false,
  blob_count_test: false,
  test_total_area_min: 0,
  test_total_area_max: 1e12,
  test_blob_count_min: 0,
  test_blob_count_max: 1000000,
  contour_chain: 'SIMPLE',
  approx_epsilon_ratio: 0.01,
  polygon_max_points: 0
})

watch(selectedItem, () => {
  if (!isBlobSelected.value) return
  const it = selectedItem.value || {}
  const def = selectedDef.value || {}
  const src = { ...def, ...it }
  blobParams.value = {
    inspec_pass_fail: !!src.inspec_pass_fail,
    th_min: toNumber(src.th_min),
    th_max: toNumber(src.th_max, 255),
    area_min: toNumber(src.area_min, 0, true),
    area_max: toNumber(src.area_max, 1e12, true),
    total_area_test: !!src.total_area_test,
    blob_count_test: !!src.blob_count_test,
    test_total_area_min: toNumber(src.test_total_area_min, 0, true),
    test_total_area_max: toNumber(src.test_total_area_max, 1e12, true),
    test_blob_count_min: toNumber(src.test_blob_count_min, 0),
    test_blob_count_max: toNumber(src.test_blob_count_max, 1000000),
    contour_chain: String(src.contour_chain || 'SIMPLE').toUpperCase(),
    approx_epsilon_ratio: toFloat(src.approx_epsilon_ratio, 0.01),
    polygon_max_points: toNumber(src.polygon_max_points, 0)
  }
}, { immediate: true })

function toNumber(v, def = 0, allowFloat = false) {
  const n = allowFloat ? parseFloat(v) : parseInt(v)
  return Number.isFinite(n) ? n : def
}
function toFloat(v, def = 0) {
  const n = parseFloat(v)
  return Number.isFinite(n) ? n : def
}

function updateBlobParam(key, value) {
  if (props.readOnly) return
  blobParams.value[key] = value
  if (selectedIndex.value < 0) return
  emit('update-tool-param', { index: selectedIndex.value, key, value })
}

const { getParam, selectedToolType } = useToolParams(selectedItem, selectedDef)

const activeParams = computed(() => {
  const t = selectedToolType.value
  if (t === 'blob') return blobParams.value
  if (t === 'grayscale') return {
    method: getParam('method', 'luminance'),
    normalize: !!getParam('normalize', false)
  }
  if (t === 'blur') return {
    method: getParam('method', 'gaussian'),
    ksize: toNumber(getParam('ksize', 3)),
    sigma: toFloat(getParam('sigma', 0))
  }
  if (t === 'threshold') return {
    mode: getParam('mode', 'binary'),
    th_min: toNumber(getParam('th_min', 0)),
    th_max: toNumber(getParam('th_max', 255))
  }
  if (t === 'morphology') return {
    kernel: toNumber(getParam('kernel', 3)),
    open: toNumber(getParam('open', 0)),
    close: toNumber(getParam('close', 0)),
    shape: String(getParam('shape', 'ellipse'))
  }
  if (t === 'math') return {
    operation: String(getParam('operation', '')),
    reference_tool_id: toNumber(getParam('reference_tool_id', null)),
    custom_formula: String(getParam('custom_formula', ''))
  }
  return {}
})

function onParamsUpdate({ key, value }) {
  // Atualização imediata do overlay quando ROI muda via parâmetros
  if (key === 'ROI' && value && typeof value === 'object') {
    if (value.shape === 'rect' && value.rect) {
      selectedRoi.value = { ...value.rect }
      selectedRoiShape.value = { shape: 'rect', rect: { ...value.rect } }
    } else if (value.shape === 'circle' && value.circle) {
      selectedRoi.value = null
      selectedRoiShape.value = { shape: 'circle', circle: { ...value.circle } }
    } else if (value.shape === 'ellipse' && value.ellipse) {
      selectedRoi.value = null
      selectedRoiShape.value = { shape: 'ellipse', ellipse: { ...value.ellipse } }
    }
    // Monta JSON completo e loga
    const full = buildInspectionPayload({ applyRoiAtIndex: selectedIndex.value, roiValue: value })
    try { lastSentJson.value = JSON.stringify(full, null, 2) } catch { lastSentJson.value = String(full) }
    // Propaga mudança para o pai para envio à VM
    emit('update-tool-param', { index: -1, key: 'INSPECTION_CONFIG', value: full })
    if (selectedIndex.value < 0 && displayItems.value.length > 0) {
      selectedIndex.value = 0
    }
    if (selectedIndex.value >= 0) {
      emitParam('INSPECTION_CONFIG', full)
    }
    return
  }

  if (selectedToolType.value === 'blob') {
    updateBlobParam(key, value)
  } else {
    emitParam(key, value)
  }
}

// seleção de tipo agora via selectedToolType

// listas de opções movidas para ToolParamsPanel

// getParam agora fornecido por useToolParams

function emitParam(key, value) {
  if (props.readOnly) return
  if (selectedIndex.value < 0) return
  const payload = { index: selectedIndex.value, key, value }
  
  emit('update-tool-param', payload)
}

function onRoiChange(newShape) {
  if (props.readOnly) return
  if (selectedIndex.value < 0) return
  // Atualiza estado local para feedback imediato
  if (newShape?.shape === 'rect' && newShape.rect) {
    selectedRoi.value = { ...newShape.rect }
    selectedRoiShape.value = { shape: 'rect', rect: { ...newShape.rect } }
    emitParam('ROI', { shape: 'rect', rect: { ...newShape.rect } })
  } else if (newShape?.shape === 'circle' && newShape.circle) {
    selectedRoi.value = null
    selectedRoiShape.value = { shape: 'circle', circle: { ...newShape.circle } }
    emitParam('ROI', { shape: 'circle', circle: { ...newShape.circle } })
  } else if (newShape?.shape === 'ellipse' && newShape.ellipse) {
    selectedRoi.value = null
    selectedRoiShape.value = { shape: 'ellipse', ellipse: { ...newShape.ellipse } }
    emitParam('ROI', { shape: 'ellipse', ellipse: { ...newShape.ellipse } })
  }
}

function onAddTool(newTool) {
  // Encaminha para a view hospedeira adicionar no final
  // Nesta emissão, index: -1 para indicar operação na lista e key: 'ADD_TOOL'
  const payload = { index: -1, key: 'ADD_TOOL', value: newTool }
  emit('update-tool-param', payload)
}

function onReorderExternal({ orderIndexes, deleteIndexes, composePlan }) {
  if (!Array.isArray(orderIndexes)) return
  // Emite para a view hospedeira a nova ordem e exclusões pendentes
  emit('update-tool-param', { index: -1, key: 'INSPECTION_REORDER', value: { orderIndexes, deleteIndexes: Array.isArray(deleteIndexes) ? deleteIndexes : [], composePlan: Array.isArray(composePlan) ? composePlan : [] } })
}
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

.blob-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}
.blob-table th, .blob-table td {
  border: 1px solid #e9ecef;
  padding: 6px 8px;
}
.blob-table thead th {
  background: #f1f3f5;
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

.tools-header {
  font-weight: 600;
  padding: 10px 12px;
  border-bottom: 1px solid #e9ecef;
}

.debug-jsons {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}
@media (min-width: 992px) {
  .debug-jsons { grid-template-columns: 1fr 1fr; }
}
.debug-block { border: 1px solid #e9ecef; border-radius: 10px; background: #fff; }
.debug-textarea {
  width: 100%;
  min-height: 160px;
  border: 0;
  outline: 0;
  padding: 10px 12px;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  font-size: 0.85rem;
  background: #0b1520;
  color: #cfe8ff;
  border-radius: 0 0 10px 10px;
}
</style>


