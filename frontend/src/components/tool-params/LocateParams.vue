<template>
  <div class="locate-params">
    <div class="section-title">Parâmetros da Locate</div>
    <div class="row g-2">
      <div class="col-12">
        <div class="small text-muted mb-1">Seta (pontos em coordenadas da imagem; o sentido é p0 → p1)</div>
      </div>
      <div class="col-6 col-md-3">
        <FormKit type="number" :label="'p0.x'" :step="1" :disabled="readOnly"
          :model-value="arrowModel.p0.x" @input="v=>onArrowField('p0','x', v)" />
      </div>
      <div class="col-6 col-md-3">
        <FormKit type="number" :label="'p0.y'" :step="1" :disabled="readOnly"
          :model-value="arrowModel.p0.y" @input="v=>onArrowField('p0','y', v)" />
      </div>
      <div class="col-6 col-md-3">
        <FormKit type="number" :label="'p1.x'" :step="1" :disabled="readOnly"
          :model-value="arrowModel.p1.x" @input="v=>onArrowField('p1','x', v)" />
      </div>
      <div class="col-6 col-md-3">
        <FormKit type="number" :label="'p1.y'" :step="1" :disabled="readOnly"
          :model-value="arrowModel.p1.y" @input="v=>onArrowField('p1','y', v)" />
      </div>

      <div class="col-12 col-md-4">
        <FormKit type="select" :label="'Modo de limiar'" :options="modes" :disabled="readOnly"
          :model-value="String(params.threshold_mode || 'fixed')" @input="v=>emitChange('threshold_mode', toStr(v,'fixed'))" />
      </div>
      <div class="col-12 col-md-4">
        <FormKit type="number" :label="'Threshold'" :step="1" :disabled="readOnly || String(params.threshold_mode||'fixed')!=='fixed'"
          :model-value="localThreshold" @input="onThresholdInput" />
      </div>
      <div class="col-12 col-md-4">
        <FormKit type="number" :label="'adaptive_k'" :step="0.1" :disabled="readOnly || String(params.threshold_mode||'fixed')!=='adaptive'"
          :model-value="toFloat(params.adaptive_k, 1.0)" @input="v=>emitChange('adaptive_k', toFloat(v, 1.0))" />
      </div>

      <div class="col-12 col-md-4">
        <FormKit type="select" :label="'Polaridade'" :options="polarities" :disabled="readOnly"
          :model-value="String(params.polaridade || 'any')" @input="v=>emitChange('polaridade', toStr(v,'any'))" />
      </div>
      <div class="col-12 col-md-4">
        <FormKit type="select" :label="'Seleção'" :options="edgeSelectOptions" :disabled="readOnly"
          :model-value="String(params.edge_select || 'strongest')" @input="v=>emitChange('edge_select', toStr(v,'strongest'))" />
      </div>
      <div class="col-6 col-md-2">
        <FormKit type="number" :label="'smooth_ksize'" :step="1" :disabled="readOnly"
          :model-value="toOdd(params.smooth_ksize, 5)" @input="v=>emitChange('smooth_ksize', toOdd(v,5))" />
      </div>
      <div class="col-6 col-md-2">
        <FormKit type="number" :label="'grad_kernel'" :step="2" :disabled="readOnly"
          :model-value="toKernel(params.grad_kernel, 3)" @input="v=>emitChange('grad_kernel', toKernel(v,3))" />
      </div>
      <div class="col-12 col-md-4 d-flex align-items-end">
        <FormKit type="checkbox" :label="'Aplicar transformação (dx, dy, θ) nos ROIs seguintes'" :disabled="readOnly"
          :model-value="!!params.apply_transform" @input="v=>emitChange('apply_transform', !!v)" />
      </div>
      <div class="col-12 col-md-4 d-flex align-items-end">
        <FormKit type="checkbox" :label="'rotate'" :disabled="readOnly"
          :model-value="!!params.rotate" @input="v=>emitChange('rotate', !!v)" />
      </div>
      <div class="col-12 col-md-4 d-flex align-items-end">
        <button class="btn btn-outline-primary w-100" type="button" :disabled="readOnly" @click="onSyncReference">
          Definir referência (usar resultado atual)
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits, ref, watch } from 'vue'

const props = defineProps({
  params: { type: Object, default: () => ({}) },
  readOnly: { type: Boolean, default: true },
  polarities: { type: Array, default: () => ([
    { value: 'any', label: 'any' },
    { value: 'dark_to_light', label: 'dark_to_light' },
    { value: 'light_to_dark', label: 'light_to_dark' }
  ]) },
  edgeSelectOptions: { type: Array, default: () => ([
    { value: 'strongest', label: 'strongest' },
    { value: 'first', label: 'first' },
    { value: 'closest_to_mid', label: 'closest_to_mid' }
  ]) },
  modes: { type: Array, default: () => ([
    { value: 'fixed', label: 'fixed' },
    { value: 'adaptive', label: 'adaptive' }
  ]) }
})
const emit = defineEmits(['change'])

function emitChange(key, value) { emit('change', { key, value }) }
function toNum(v, d=0) { const n = parseFloat(v); return Number.isFinite(n) ? n : d }
function toFloat(v, d=0) { const n = parseFloat(v); return Number.isFinite(n) ? n : d }
function toStr(v, d='') { const s = typeof v === 'string' ? v : v?.target?.value; return s ?? d }
function toOdd(v, d=5) { let n = Math.max(1, Math.round(toNum(v,d))); if (n % 2 === 0) n += 1; return n }
function toKernel(v, d=3) { const n = Math.round(toNum(v,d)); return [1,3,5,7].includes(n) ? n : d }

const arrowModel = ref({ p0: { x: 0, y: 0 }, p1: { x: 0, y: 0 } })
const localThreshold = ref(20)
function syncArrow() {
  const a = (typeof props.params === 'object' && props.params && props.params.arrow) ? props.params.arrow : {}
  const p0 = a?.p0 || {}
  const p1 = a?.p1 || {}
  arrowModel.value = {
    p0: { x: toNum(p0.x, 0), y: toNum(p0.y, 0) },
    p1: { x: toNum(p1.x, 0), y: toNum(p1.y, 0) }
  }
}
watch(() => props.params, () => { syncArrow() }, { immediate: true, deep: true })

function onArrowField(which, key, v) {
  if (props.readOnly) return
  const nv = toNum(v, 0)
  arrowModel.value = {
    ...arrowModel.value,
    [which]: { ...arrowModel.value[which], [key]: nv }
  }
  emitChange('arrow', {
    p0: { x: arrowModel.value.p0.x, y: arrowModel.value.p0.y },
    p1: { x: arrowModel.value.p1.x, y: arrowModel.value.p1.y }
  })
}

watch(() => props.params, () => {
  localThreshold.value = toNum(props.params?.threshold, props.params?.th_min ?? 20)
}, { immediate: true, deep: true })

function onThresholdInput(v) {
  const nv = toNum(v, localThreshold.value)
  localThreshold.value = nv
  emitChange('threshold', nv)
}

function onSyncReference() {
  // Sinaliza ao host para sincronizar a referência com o resultado atual
  emitChange('reference', '__SYNC_REFERENCE__')
}
</script>

<style scoped>
.section-title { font-weight: 600; margin: 8px 0; }
</style>


