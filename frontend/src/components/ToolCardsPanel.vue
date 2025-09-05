<template>
  <div class="tools-panel" v-if="items && items.length">
    <div class="tools-header">Ciclo de Inspeção</div>
    <div class="tools-grid">
      <div
        v-for="(item, idx) in items"
        :key="itemKey(item, idx)"
        class="tool-card"
        :title="cardTitle(item)"
        @click="onClick(idx)"
        :class="{ selected: selectedIndex === idx }"
      >
        <div class="status-dot" :class="statusClass(item)"></div>
        <div class="tool-name">{{ cardName(item) }}</div>
        <div class="tool-type">{{ cardType(item) }}</div>
        <div class="tool-meta" v-if="item?.processing_time_ms !== undefined">{{ item.processing_time_ms }} ms</div>
      </div>
    </div>
  </div>
  <div v-else></div>
  
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  items: { type: Array, default: () => [] },
  selectedIndex: { type: Number, default: -1 }
})

const emit = defineEmits(['select'])

function itemKey(item, idx) {
  const base = String(item?.id ?? item?.name ?? item?.type ?? '')
  return base || `idx_${idx}`
}
function cardTitle(item) { return cardName(item) || cardType(item) }
function cardName(item) { return item?.name || item?.tool_name || 'Sem nome' }
function cardType(item) { return item?.type || item?.tool_type || '—' }
function extractPassFail(item) {
  if (typeof item?.pass_fail === 'boolean') return item.pass_fail
  const candidates = []
  if (item?.test) candidates.push(item.test)
  if (Array.isArray(item?.tests)) candidates.push(...item.tests)
  for (const t of candidates) {
    if (t && typeof t === 'object') {
      if (typeof t.pass_fail === 'boolean') return t.pass_fail
      if (typeof t.passed === 'boolean') return t.passed
      if (typeof t.ok === 'boolean') return t.ok
    }
  }
  return undefined
}
function statusClass(item) {
  const pf = extractPassFail(item)
  if (pf === true) return 'status-pass'
  if (pf === false) return 'status-fail'
  return 'status-unknown'
}
function onClick(idx) { emit('select', idx) }

</script>

<style scoped>
.mt-3 { margin-top: 1rem; }
.tools-panel {
  border: 1px solid #e9ecef;
  border-radius: 10px;
  background: #fff;
}
.tools-header {
  font-weight: 600;
  padding: 10px 12px;
  border-bottom: 1px solid #e9ecef;
}
.tools-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 8px;
}
.tool-card {
  aspect-ratio: 1 / 1;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #fff;
  cursor: pointer;
  transition: border-color .15s ease, box-shadow .15s ease, transform .05s ease;
  position: relative;
}
.tool-card:hover {
  border-color: #cfe2ff;
  box-shadow: 0 2px 8px rgba(13,110,253,.1);
}
.tool-card.selected {
  border-color: #0d6efd;
  box-shadow: 0 0 0 2px rgba(13,110,253,.2);
}
.tool-name { font-weight: 600; font-size: 0.95rem; }
.tool-type { color: #6c757d; font-size: 0.85rem; }
.tool-meta { margin-top: 4px; font-size: 0.8rem; color: #6c757d; }
.status-dot { position: absolute; top: 8px; left: 8px; width: 10px; height: 10px; border-radius: 50%; box-shadow: 0 0 0 2px #fff; }
.status-pass { background: #198754; }
.status-fail { background: #dc3545; }
.status-unknown { background: #adb5bd; }
</style>


