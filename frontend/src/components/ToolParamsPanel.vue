<template>
  <FormKit type="form" :actions="false">
    <div class="form-section">
      <div class="section-title">Geral</div>
      <div class="row g-2 mb-2">
        <div class="col-12 col-md-6">
          <FormKit type="text" :label="'Nome da ferramenta'" :disabled="readOnly"
            :model-value="toolName" @input="onNameInput" />
        </div>
        <div class="col-12 col-md-6">
          <div class="small mt-4 name-error" v-if="nameError">{{ nameError }}</div>
        </div>
      </div>
      <div class="section-title">Região de Interesse (ROI)</div>
      <div class="row g-2 mb-2">
        <div class="col-12 col-md-6">
          <FormKit type="select" :label="'Shape'" :options="shapeOptions" :disabled="readOnly"
            :model-value="roiModel.shape" @input="onShapeChange" />
        </div>
        <template v-if="roiModel.shape === 'rect'">
          <div class="col-6 col-md-3"><FormKit type="number" :label="'x'" :step="1" :disabled="readOnly" :model-value="roiModel.rect.x" @input="v=>onRectField('x', v)" /></div>
          <div class="col-6 col-md-3"><FormKit type="number" :label="'y'" :step="1" :disabled="readOnly" :model-value="roiModel.rect.y" @input="v=>onRectField('y', v)" /></div>
          <div class="col-6 col-md-3"><FormKit type="number" :label="'w'" :step="1" :disabled="readOnly" :model-value="roiModel.rect.w" @input="v=>onRectField('w', v)" /></div>
          <div class="col-6 col-md-3"><FormKit type="number" :label="'h'" :step="1" :disabled="readOnly" :model-value="roiModel.rect.h" @input="v=>onRectField('h', v)" /></div>
        </template>
        <template v-else-if="roiModel.shape === 'circle'">
          <div class="col-6 col-md-4"><FormKit type="number" :label="'cx'" :step="1" :disabled="readOnly" :model-value="roiModel.circle.cx" @input="v=>onCircleField('cx', v)" /></div>
          <div class="col-6 col-md-4"><FormKit type="number" :label="'cy'" :step="1" :disabled="readOnly" :model-value="roiModel.circle.cy" @input="v=>onCircleField('cy', v)" /></div>
          <div class="col-12 col-md-4"><FormKit type="number" :label="'r'" :step="1" :disabled="readOnly" :model-value="roiModel.circle.r" @input="v=>onCircleField('r', v)" /></div>
        </template>
        <template v-else-if="roiModel.shape === 'ellipse'">
          <div class="col-6 col-md-3"><FormKit type="number" :label="'cx'" :step="1" :disabled="readOnly" :model-value="roiModel.ellipse.cx" @input="v=>onEllipseField('cx', v)" /></div>
          <div class="col-6 col-md-3"><FormKit type="number" :label="'cy'" :step="1" :disabled="readOnly" :model-value="roiModel.ellipse.cy" @input="v=>onEllipseField('cy', v)" /></div>
          <div class="col-6 col-md-2"><FormKit type="number" :label="'rx'" :step="1" :disabled="readOnly" :model-value="roiModel.ellipse.rx" @input="v=>onEllipseField('rx', v)" /></div>
          <div class="col-6 col-md-2"><FormKit type="number" :label="'ry'" :step="1" :disabled="readOnly" :model-value="roiModel.ellipse.ry" @input="v=>onEllipseField('ry', v)" /></div>
          <div class="col-12 col-md-2"><FormKit type="number" :label="'angle'" :step="1" :disabled="readOnly" :model-value="roiModel.ellipse.angle" @input="v=>onEllipseField('angle', v)" /></div>
        </template>
      </div>

      <component
        :is="activeComp"
        v-if="activeComp"
        :params="params"
        :read-only="readOnly"
        v-bind="extraProps"
        @change="onChange"
      />
      <template v-else>
        <div class="text-muted small mb-2">Parâmetros desta ferramenta são somente leitura aqui.</div>
      </template>
    </div>
  </FormKit>
  
</template>

<script setup>
import { computed, defineProps, defineEmits, ref, watch } from 'vue'
import BlobParams from '@/components/tool-params/BlobParams.vue'
import GrayscaleParams from '@/components/tool-params/GrayscaleParams.vue'
import BlurParams from '@/components/tool-params/BlurParams.vue'
import ThresholdParams from '@/components/tool-params/ThresholdParams.vue'
import MorphologyParams from '@/components/tool-params/MorphologyParams.vue'
import MathParams from '@/components/tool-params/MathParams.vue'
import LocateParams from '@/components/tool-params/LocateParams.vue'

const props = defineProps({
  type: { type: String, default: '' },
  params: { type: Object, default: () => ({}) },
  readOnly: { type: Boolean, default: true },
  roi: { type: Object, default: null },
  allNames: { type: Array, default: () => [] },
  currentName: { type: String, default: '' }
})
const emit = defineEmits(['update'])

const contourOptions = [
  { value: 'SIMPLE', label: 'SIMPLE' },
  { value: 'NONE', label: 'NONE' },
  { value: 'TC89_L1', label: 'TC89_L1' },
  { value: 'TC89_KCOS', label: 'TC89_KCOS' }
]
const grayscaleMethods = [
  { value: 'luminance', label: 'luminance' },
  { value: 'average', label: 'average' },
  { value: 'weighted', label: 'weighted' }
]
const blurMethods = [
  { value: 'gaussian', label: 'gaussian' },
  { value: 'median', label: 'median' }
]
const thresholdModes = [
  { value: 'binary', label: 'binary' },
  { value: 'range', label: 'range' },
  { value: 'otsu', label: 'otsu' }
]
const morphShapes = [
  { value: 'ellipse', label: 'ellipse' },
  { value: 'rect', label: 'rect' },
  { value: 'cross', label: 'cross' }
]
const mathOps = [
  { value: 'area_ratio', label: 'area_ratio' },
  { value: 'blob_density', label: 'blob_density' },
  { value: 'custom_formula', label: 'custom_formula' }
]

const normalizedType = computed(() => String(props.type || '').toLowerCase())

const toolName = ref('')
const nameError = ref('')
watch(() => props.currentName, (v) => { toolName.value = String(v || '') }, { immediate: true })
function onNameInput(val) {
  if (props.readOnly) return
  let nv = typeof val === 'string' ? val : val?.target?.value
  // normalizar: remover acentos, manter [a-zA-Z0-9_], trocar espaços por underscore, colapsar múltiplos _
  nv = String(nv || '')
    .normalize('NFD').replace(/\p{Diacritic}+/gu, '')
    .replace(/\s+/g, '_')
    .replace(/[^a-zA-Z0-9_]/g, '_')
    .replace(/_+/g, '_')
    .replace(/^_+|_+$/g, '')
  toolName.value = nv
  // validação de unicidade
  const exists = (props.allNames || []).filter(n => String(n) === String(nv))
  const isDuplicate = exists.length > 0 && String(nv) !== String(props.currentName)
  nameError.value = isDuplicate ? 'Nome já utilizado. Escolha outro.' : ''
  if (!isDuplicate && nv && nv.trim()) {
    emit('update', { key: 'name', value: nv })
  }
}

const shapeOptions = [
  { value: 'rect', label: 'retângulo' },
  { value: 'circle', label: 'círculo' },
  { value: 'ellipse', label: 'elipse' }
]

const roiModel = ref({
  shape: 'rect',
  rect: { x: 0, y: 0, w: 100, h: 100 },
  circle: { cx: 50, cy: 50, r: 50 },
  ellipse: { cx: 60, cy: 60, rx: 40, ry: 30, angle: 0 }
})

function syncFromProps() {
  const r = props.roi || null
  if (!r || typeof r !== 'object') return
  if (r.shape === 'rect' && r.rect) {
    roiModel.value.shape = 'rect'
    roiModel.value.rect = { x: +r.rect.x || 0, y: +r.rect.y || 0, w: +r.rect.w || 0, h: +r.rect.h || 0 }
  } else if (r.shape === 'circle' && r.circle) {
    roiModel.value.shape = 'circle'
    roiModel.value.circle = { cx: +r.circle.cx || 0, cy: +r.circle.cy || 0, r: +r.circle.r || 0 }
  } else if (r.shape === 'ellipse' && r.ellipse) {
    roiModel.value.shape = 'ellipse'
    roiModel.value.ellipse = { cx: +r.ellipse.cx || 0, cy: +r.ellipse.cy || 0, rx: +r.ellipse.rx || 0, ry: +r.ellipse.ry || 0, angle: +r.ellipse.angle || 0 }
  }
}

watch(() => props.roi, () => { syncFromProps() }, { immediate: true, deep: true })

function emitRoi() {
  if (props.readOnly) return
  const s = roiModel.value.shape
  if (s === 'rect') {
    emit('update', { key: 'ROI', value: { shape: 'rect', rect: { ...roiModel.value.rect } } })
  } else if (s === 'circle') {
    emit('update', { key: 'ROI', value: { shape: 'circle', circle: { ...roiModel.value.circle } } })
  } else if (s === 'ellipse') {
    emit('update', { key: 'ROI', value: { shape: 'ellipse', ellipse: { ...roiModel.value.ellipse } } })
  }
}

function onShapeChange(val) {
  if (props.readOnly) return
  const newShape = typeof val === 'string' ? val : val?.target?.value
  if (!newShape) return
  roiModel.value.shape = newShape
  emitRoi()
}

function toNum(v) { const n = parseFloat(v); return Number.isFinite(n) ? n : 0 }
function onRectField(k, v) { if (props.readOnly) return; roiModel.value.rect[k] = toNum(v); emitRoi() }
function onCircleField(k, v) { if (props.readOnly) return; roiModel.value.circle[k] = toNum(v); emitRoi() }
function onEllipseField(k, v) { if (props.readOnly) return; roiModel.value.ellipse[k] = toNum(v); emitRoi() }

const activeComp = computed(() => {
  switch (normalizedType.value) {
    case 'blob': return BlobParams
    case 'grayscale': return GrayscaleParams
    case 'blur': return BlurParams
    case 'threshold': return ThresholdParams
    case 'morphology': return MorphologyParams
    case 'math': return MathParams
    case 'locate': return LocateParams
    default: return null
  }
})

const extraProps = computed(() => {
  switch (normalizedType.value) {
    case 'blob': return { contourOptions }
    case 'grayscale': return { methods: grayscaleMethods }
    case 'blur': return { methods: blurMethods }
    case 'threshold': return { modes: thresholdModes }
    case 'morphology': return { shapes: morphShapes }
    case 'math': return { ops: mathOps }
    default: return {}
  }
})

function onChange({ key, value }) {
  emit('update', { key, value })
}
 </script>

<style scoped>
.name-error { color: #dc3545; }
</style>
