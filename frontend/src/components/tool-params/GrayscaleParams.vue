<template>
  <div>
    <h6 class="section-subtitle">Grayscale</h6>
    <div class="row g-2 mb-2">
      <div class="col-12 col-md-6">
        <FormKit type="select" :options="methods" label="method" :model-value="params.method" :disabled="readOnly" @update:modelValue="v=>emitChange('method', String(v||'luminance'))" />
      </div>
      <div class="col-12 col-md-6 d-flex align-items-end">
        <FormKit type="checkbox" label="normalize" :model-value="!!params.normalize" :disabled="readOnly" @update:modelValue="v=>emitChange('normalize', !!v)" />
      </div>
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
function emitChange(key, value) {
  if (props.readOnly) return
  emit('change', { key, value })
}
</script>
