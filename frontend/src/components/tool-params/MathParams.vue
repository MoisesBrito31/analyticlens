<template>
  <div>
    <h6 class="section-subtitle">Math</h6>
    <div class="row g-2 mb-2">
      <div class="col-12 col-md-4"><FormKit type="select" :options="ops" label="operation" :model-value="params.operation" :disabled="readOnly" @update:modelValue="v=>emitChange('operation', String(v||''))" /></div>
      <div class="col-12 col-md-4"><FormKit type="number" label="reference_tool_id" :model-value="params.reference_tool_id" :disabled="readOnly" @update:modelValue="v=>emitChange('reference_tool_id', toInt(v))" /></div>
      <div class="col-12 col-md-4"><FormKit type="text" label="custom_formula" :model-value="params.custom_formula" :disabled="readOnly" @update:modelValue="v=>emitChange('custom_formula', String(v||''))" /></div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  params: { type: Object, required: true },
  readOnly: { type: Boolean, default: true },
  ops: { type: Array, default: () => [] }
})
const emit = defineEmits(['change'])
function toInt(v, def = 0) { const n = parseInt(v); return Number.isFinite(n) ? n : def }
function emitChange(key, value) { if (props.readOnly) return; emit('change', { key, value }) }
</script>
