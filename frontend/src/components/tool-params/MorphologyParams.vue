<template>
  <div>
    <h6 class="section-subtitle">Morphology</h6>
    <div class="row g-2 mb-2">
      <div class="col-12 col-md-3"><FormKit type="number" label="kernel" :model-value="params.kernel" :disabled="readOnly" @update:modelValue="v=>emitChange('kernel', toInt(v))" /></div>
      <div class="col-12 col-md-3"><FormKit type="number" label="open" :model-value="params.open" :disabled="readOnly" @update:modelValue="v=>emitChange('open', toInt(v))" /></div>
      <div class="col-12 col-md-3"><FormKit type="number" label="close" :model-value="params.close" :disabled="readOnly" @update:modelValue="v=>emitChange('close', toInt(v))" /></div>
      <div class="col-12 col-md-3"><FormKit type="select" :options="shapes" label="shape" :model-value="params.shape" :disabled="readOnly" @update:modelValue="v=>emitChange('shape', String(v||'ellipse'))" /></div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  params: { type: Object, required: true },
  readOnly: { type: Boolean, default: true },
  shapes: { type: Array, default: () => [] }
})
const emit = defineEmits(['change'])
function toInt(v, def = 0) { const n = parseInt(v); return Number.isFinite(n) ? n : def }
function emitChange(key, value) { if (props.readOnly) return; emit('change', { key, value }) }
</script>
