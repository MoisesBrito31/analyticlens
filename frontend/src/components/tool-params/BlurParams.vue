<template>
  <div>
    <h6 class="section-subtitle">Blur</h6>
    <div class="row g-2 mb-2">
      <div class="col-12 col-md-4"><FormKit type="select" :options="methods" label="method" :model-value="params.method" :disabled="readOnly" @update:modelValue="v=>emitChange('method', String(v||'gaussian'))" /></div>
      <div class="col-12 col-md-4"><FormKit type="number" label="ksize" :model-value="params.ksize" :disabled="readOnly" @update:modelValue="v=>emitChange('ksize', toInt(v))" /></div>
      <div class="col-12 col-md-4"><FormKit type="number" step="0.01" label="sigma" :model-value="params.sigma" :disabled="readOnly" @update:modelValue="v=>emitChange('sigma', toFloat(v))" /></div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  params: { type: Object, required: true },
  readOnly: { type: Boolean, default: true },
  methods: { type: Array, default: () => [] }
})
const emit = defineEmits(['change'])
function toInt(v, def = 0) { const n = parseInt(v); return Number.isFinite(n) ? n : def }
function toFloat(v, def = 0) { const n = parseFloat(v); return Number.isFinite(n) ? n : def }
function emitChange(key, value) { if (props.readOnly) return; emit('change', { key, value }) }
</script>
