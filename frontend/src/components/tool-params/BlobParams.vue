<template>
  <div>
    <h6 class="section-subtitle">Blob - Parâmetros</h6>
    <div class="row g-2 mb-2">
      <div class="col-12">
        <FormKit type="checkbox" label="Considerar no resultado (inspec_pass_fail)" :model-value="!!params.inspec_pass_fail" :disabled="readOnly" @update:modelValue="v=>emitChange('inspec_pass_fail', !!v)" />
      </div>
    </div>
    <div class="row g-2 mb-2">
      <div class="col-6 col-md-3"><FormKit type="number" label="th_min" :model-value="params.th_min" :disabled="readOnly" @update:modelValue="v=>emitChange('th_min', toInt(v))" /></div>
      <div class="col-6 col-md-3"><FormKit type="number" label="th_max" :model-value="params.th_max" :disabled="readOnly" @update:modelValue="v=>emitChange('th_max', toInt(v))" /></div>
      <div class="col-6 col-md-3"><FormKit type="number" label="area_min" :model-value="params.area_min" :disabled="readOnly" @update:modelValue="v=>emitChange('area_min', toFloat(v))" /></div>
      <div class="col-6 col-md-3"><FormKit type="number" label="area_max" :model-value="params.area_max" :disabled="readOnly" @update:modelValue="v=>emitChange('area_max', toFloat(v))" /></div>
    </div>
    <div class="row g-2 mb-2">
      <div class="col-6 col-md-3"><FormKit type="checkbox" label="total_area_test" :model-value="!!params.total_area_test" :disabled="readOnly" @update:modelValue="v=>emitChange('total_area_test', !!v)" /></div>
      <div class="col-6 col-md-3"><FormKit type="checkbox" label="blob_count_test" :model-value="!!params.blob_count_test" :disabled="readOnly" @update:modelValue="v=>emitChange('blob_count_test', !!v)" /></div>
      <div class="col-6 col-md-3"><FormKit type="number" label="test_total_area_min" :model-value="params.test_total_area_min" :disabled="readOnly" @update:modelValue="v=>emitChange('test_total_area_min', toFloat(v))" /></div>
      <div class="col-6 col-md-3"><FormKit type="number" label="test_total_area_max" :model-value="params.test_total_area_max" :disabled="readOnly" @update:modelValue="v=>emitChange('test_total_area_max', toFloat(v))" /></div>
    </div>
    <div class="row g-2 mb-2">
      <div class="col-6 col-md-3"><FormKit type="number" label="test_blob_count_min" :model-value="params.test_blob_count_min" :disabled="readOnly" @update:modelValue="v=>emitChange('test_blob_count_min', toInt(v))" /></div>
      <div class="col-6 col-md-3"><FormKit type="number" label="test_blob_count_max" :model-value="params.test_blob_count_max" :disabled="readOnly" @update:modelValue="v=>emitChange('test_blob_count_max', toInt(v))" /></div>
      <div class="col-6 col-md-3"><FormKit type="select" :options="contourOptions" label="contour_chain" :model-value="params.contour_chain" :disabled="readOnly" @update:modelValue="v=>emitChange('contour_chain', String(v||'SIMPLE'))" /></div>
      <div class="col-6 col-md-3"><FormKit type="number" step="0.001" label="approx_epsilon_ratio" :model-value="params.approx_epsilon_ratio" :disabled="readOnly" @update:modelValue="v=>emitChange('approx_epsilon_ratio', toFloat(v))" /></div>
    </div>
    <div class="row g-2 mb-2">
      <div class="col-6 col-md-3"><FormKit type="number" label="polygon_max_points" :model-value="params.polygon_max_points" :disabled="readOnly" @update:modelValue="v=>emitChange('polygon_max_points', toInt(v))" /></div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  params: { type: Object, required: true },
  readOnly: { type: Boolean, default: true },
  contourOptions: { type: Array, default: () => [] }
})

const emit = defineEmits(['change'])

function toInt(v, def = 0) {
  const n = parseInt(v)
  return Number.isFinite(n) ? n : def
}
function toFloat(v, def = 0) {
  const n = parseFloat(v)
  return Number.isFinite(n) ? n : def
}
function emitChange(key, value) {
  if (props.readOnly) return
  emit('change', { key, value })
}
</script>
