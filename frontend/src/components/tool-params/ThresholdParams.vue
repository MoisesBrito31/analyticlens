<template>
  <div>
    <h6 class="section-subtitle">Threshold</h6>
    <div class="row g-2 mb-2">
      <div class="col-12 col-md-4"><FormKit type="select" :options="modes" label="mode" :model-value="params.mode" :disabled="readOnly" @update:modelValue="v=>emitChange('mode', String(v||'binary'))" /></div>
      <div class="col-12 col-md-4"><FormKit type="number" label="th_min" :model-value="params.th_min" :disabled="readOnly" @update:modelValue="v=>emitChange('th_min', toInt(v))" /></div>
      <div class="col-12 col-md-4"><FormKit type="number" label="th_max" :model-value="params.th_max" :disabled="readOnly" @update:modelValue="v=>emitChange('th_max', toInt(v))" /></div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  params: { type: Object, required: true },
  readOnly: { type: Boolean, default: true },
  modes: { type: Array, default: () => [] }
})
const emit = defineEmits(['change'])
function toInt(v, def = 0) { const n = parseInt(v); return Number.isFinite(n) ? n : def }
function emitChange(key, value) { if (props.readOnly) return; emit('change', { key, value }) }
</script>
