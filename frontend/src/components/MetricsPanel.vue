<template>
  <div class="metrics-panel">
    <div class="metrics-header">Métricas</div>
    <div class="metrics-grid">
      <div class="metric"><div class="label">Aprovados</div><div class="value">{{ metrics?.aprovados ?? '—' }}</div></div>
      <div class="metric"><div class="label">Reprovados</div><div class="value">{{ metrics?.reprovados ?? '—' }}</div></div>
      <div class="metric"><div class="label">Tempo</div><div class="value">{{ metrics?.time ?? '—' }}</div></div>
      <div class="metric"><div class="label">Frame</div><div class="value">{{ metrics?.frame ?? '—' }}</div></div>
    </div>
  </div>
</template>

<script setup>
import { defineProps } from 'vue'

const props = defineProps({
  metrics: {
    type: Object,
    default: () => ({ aprovados: 0, reprovados: 0, time: '', frame: 0 })
  }
})
</script>

<style scoped>
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
</style>
