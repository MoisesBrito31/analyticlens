<template>
  <FormKit type="form" :actions="false">
    <div class="form-section">
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
import { computed, defineProps, defineEmits } from 'vue'
import BlobParams from '@/components/tool-params/BlobParams.vue'
import GrayscaleParams from '@/components/tool-params/GrayscaleParams.vue'
import BlurParams from '@/components/tool-params/BlurParams.vue'
import ThresholdParams from '@/components/tool-params/ThresholdParams.vue'
import MorphologyParams from '@/components/tool-params/MorphologyParams.vue'
import MathParams from '@/components/tool-params/MathParams.vue'

const props = defineProps({
  type: { type: String, default: '' },
  params: { type: Object, default: () => ({}) },
  readOnly: { type: Boolean, default: true }
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

const activeComp = computed(() => {
  switch (normalizedType.value) {
    case 'blob': return BlobParams
    case 'grayscale': return GrayscaleParams
    case 'blur': return BlurParams
    case 'threshold': return ThresholdParams
    case 'morphology': return MorphologyParams
    case 'math': return MathParams
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
