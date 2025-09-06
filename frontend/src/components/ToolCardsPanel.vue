<template>
  <div class="tools-panel" v-if="items && items.length">
    <div class="tools-header">Ciclo de Inspeção</div>
    <div class="tools-grid">
      <div
        v-for="(item, idx) in items"
        :key="itemKey(item, idx)"
        class="tool-card"
        :title="cardTitle(item)"
        :class="{ selected: selectedIndex === idx }"
      >
        <div class="card-body" @click="onCardBodyClick(idx)">
          <div class="status-dot" :class="statusClass(item)"></div>
          <div class="tool-name">{{ cardName(item) }}</div>
          <div class="tool-type">{{ cardType(item) }}</div>
          <div class="tool-meta" v-if="item?.processing_time_ms !== undefined">{{ item.processing_time_ms }} ms</div>
        </div>
        
      </div>
      <!-- Add new tool card -->
      <div class="tool-card add-card" :class="{ disabled: readOnly }" title="Adicionar ferramenta" @click="readOnly ? null : openAdd()">
        <div class="plus">+</div>
        <div class="tool-type">Adicionar</div>
      </div>
      <!-- Reorder tools card/button -->
      <div class="tool-card reorder-card" :class="{ disabled: readOnly }" title="Reordenar ferramentas" @click="readOnly ? null : openReorder()">
        <div class="reorder-icon">⇄</div>
        <div class="tool-type">Reordenar</div>
      </div>
    </div>
    <!-- Modal de adicionar tool -->
    <div v-if="showAdd" class="add-modal-backdrop" @click="closeAdd">
      <div class="add-modal" @click.stop>
        <div class="am-header">Adicionar ferramenta</div>
        <div class="am-grid">
          <button type="button" class="am-btn" @click="pickType('grayscale')">Grayscale</button>
          <button type="button" class="am-btn" @click="pickType('blob')">Blob</button>
          <button type="button" class="am-btn" @click="pickType('blur')">Blur</button>
          <button type="button" class="am-btn" @click="pickType('threshold')">Threshold</button>
          <button type="button" class="am-btn" @click="pickType('morphology')">Morphology</button>
          <button type="button" class="am-btn" @click="pickType('math')">Math</button>
        </div>
        <div class="am-footer">
          <button type="button" class="am-close" @click="closeAdd">Fechar</button>
        </div>
      </div>
    </div>
    <!-- Modal de reordenar tools -->
    <div v-if="showReorder" class="add-modal-backdrop" @click="closeReorder">
      <div class="add-modal reorder-modal" @click.stop>
        <div class="am-header d-flex">Reordenar ferramentas</div>
        <div class="re-grid">
          <div
            v-for="(it, i) in reorderItems"
            :key="`slot_${i}`"
            class="re-slot"
            @dragover.prevent
            @drop.prevent="onReDrop(i, $event)"
          >
            <div class="slot-badge">{{ i+1 }}º</div>
            <button type="button" class="slot-del" title="Apagar" @click.stop="onDelete(i)">×</button>
            <button type="button" class="slot-dup" title="Duplicar" @click.stop="onDuplicate(i)">⧉</button>
            <div
              class="re-tool"
              :class="{ dragging: dragging && dragFrom === i }"
              draggable="true"
              @dragstart="onReDragStart(i, $event)"
              @dragend="onReDragEnd"
              @dragover.prevent
              @drop.prevent="onReDrop(i, $event)"
            >
              <div class="re-name">{{ it.name }}</div>
              <div class="re-type">{{ it.type }}</div>
            </div>
          </div>
        </div>
        <div class="am-footer gap-2">
          <button type="button" class="am-close" @click="closeReorder">Cancelar</button>
          <button type="button" class="am-apply" @click="applyReorder">OK</button>
        </div>
      </div>
    </div>
  </div>
  <div v-else></div>
  
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  items: { type: Array, default: () => [] },
  selectedIndex: { type: Number, default: -1 },
  readOnly: { type: Boolean, default: false }
})

const emit = defineEmits(['select', 'add-tool', 'reorder'])

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
function onCardBodyClick(idx) { emit('select', idx) }

// Add tool modal
import { ref } from 'vue'
const showAdd = ref(false)
function openAdd() { showAdd.value = true }
function closeAdd() { showAdd.value = false }
function pickType(type) {
  // Define defaults by type
  const order_index = Array.isArray(props.items) ? props.items.length : 0
  const base = { order_index, name: `${type}_${order_index+1}`, type, ROI: { shape: 'rect', rect: { x: 0, y: 0, w: 100, h: 100 } }, inspec_pass_fail: false }
  if (type === 'grayscale') Object.assign(base, { method: 'luminance', normalize: false })
  if (type === 'blob') Object.assign(base, { th_min: 0, th_max: 255, area_min: 0, area_max: 1000, total_area_test: false, blob_count_test: false, test_total_area_min: 0, test_total_area_max: 1000, test_blob_count_min: 0, test_blob_count_max: 10, contour_chain: 'SIMPLE', approx_epsilon_ratio: 0, polygon_max_points: 0 })
  if (type === 'blur') Object.assign(base, { method: 'gaussian', ksize: 3, sigma: 0 })
  if (type === 'threshold') Object.assign(base, { mode: 'binary', th_min: 0, th_max: 255 })
  if (type === 'morphology') Object.assign(base, { kernel: 3, open: 0, close: 0, shape: 'ellipse' })
  if (type === 'math') Object.assign(base, { operation: '', reference_tool_id: null, custom_formula: '' })
  emit('add-tool', base)
  closeAdd()
}

// Reorder modal
const showReorder = ref(false)
const reorderItems = ref([])
const dragFrom = ref(-1)
const dragging = ref(false)
let dragGhostEl = null
const deletedMap = ref({})
function openReorder() {
  // snapshot atual: usa índice e rótulo amigável
  reorderItems.value = (Array.isArray(props.items) ? props.items : []).map((it, i) => ({
    kind: 'orig',
    index: i,
    name: it?.name || it?.tool_name || `tool_${i+1}`,
    type: it?.type || it?.tool_type || '—'
  }))
  showReorder.value = true
  deletedMap.value = {}
}
function closeReorder() { showReorder.value = false; dragFrom.value = -1; dragging.value = false }
function onReDragStart(i, evt) {
  dragFrom.value = i
  dragging.value = true
  try { evt.dataTransfer.effectAllowed = 'move'; evt.dataTransfer.setData('text/plain', String(i)) } catch {}
  try {
    // cria imagem de arrasto personalizada que seguirá o cursor
    const item = reorderItems.value[i]
    const src = evt.target && evt.target.closest ? evt.target.closest('.re-tool') : null
    const rect = src ? src.getBoundingClientRect() : { width: 120, height: 120 }
    const ghost = document.createElement('div')
    ghost.style.width = rect.width + 'px'
    ghost.style.height = rect.height + 'px'
    ghost.style.border = '2px dashed #cfe2ff'
    ghost.style.borderRadius = '8px'
    ghost.style.background = '#f8faff'
    ghost.style.display = 'flex'
    ghost.style.flexDirection = 'column'
    ghost.style.alignItems = 'center'
    ghost.style.justifyContent = 'center'
    ghost.style.fontFamily = 'inherit'
    ghost.style.pointerEvents = 'none'
    ghost.style.position = 'absolute'
    ghost.style.top = '-1000px'
    ghost.style.left = '-1000px'
    ghost.style.padding = '2px'
    const n = document.createElement('div')
    n.textContent = item?.name ?? ''
    n.style.fontWeight = '700'
    n.style.color = '#0d6efd'
    n.style.fontSize = '.9rem'
    n.style.lineHeight = '1.2'
    n.style.textAlign = 'center'
    const t = document.createElement('div')
    t.textContent = item?.type ?? ''
    t.style.color = '#6c757d'
    t.style.fontSize = '.8rem'
    t.style.lineHeight = '1.1'
    t.style.textAlign = 'center'
    ghost.appendChild(n)
    ghost.appendChild(t)
    document.body.appendChild(ghost)
    dragGhostEl = ghost
    if (evt.dataTransfer && evt.dataTransfer.setDragImage) {
      evt.dataTransfer.setDragImage(ghost, rect.width / 2, rect.height / 2)
    }
  } catch {}
}
function onReDrop(i) {
  if (dragFrom.value === -1 || i === dragFrom.value) { dragFrom.value = -1; dragging.value = false; return }
  const arr = reorderItems.value.slice()
  const [moved] = arr.splice(dragFrom.value, 1)
  arr.splice(i, 0, moved)
  reorderItems.value = arr
  dragFrom.value = -1
  dragging.value = false
}
function onReDragEnd() {
  dragging.value = false
  dragFrom.value = -1
  if (dragGhostEl && dragGhostEl.parentNode) {
    try { dragGhostEl.parentNode.removeChild(dragGhostEl) } catch {}
  }
  dragGhostEl = null
}
function applyReorder() {
  // Calcula mapeamento from->to baseado na nova ordem de índices
  // orderMap passa a referenciar posições dentro do composePlan (toda sequência visual)
  const orderMap = reorderItems.value.map((_, i) => i)
  // Emite do primeiro deslocamento que gere a ordem inteira; o container pai reconstruirá a lista
  // Para simplificar, emitimos a sequência final de índices
  const deleteIndexes = Object.keys(deletedMap.value).map(k => Number(k)).filter(n => Number.isFinite(n))
  const composePlan = reorderItems.value.map(it => ({ kind: it.kind || 'orig', index: it.index, name: it.name, type: it.type }))
  emit('reorder', { orderIndexes: orderMap, deleteIndexes, composePlan })
  closeReorder()
}

function onDelete(i) {
  const target = reorderItems.value[i]
  if (!target) return
  deletedMap.value[target.index] = true
  const arr = reorderItems.value.slice()
  arr.splice(i, 1)
  reorderItems.value = arr
}

function onDuplicate(i) {
  const src = reorderItems.value[i]
  if (!src) return
  const baseName = String(src.name || 'tool')
  const existingNames = new Set(reorderItems.value.map(x => x.name))
  let nn = `${baseName}_copy`
  let c = 2
  while (existingNames.has(nn)) { nn = `${baseName}_copy${c++}` }
  const dup = { kind: 'dup', index: src.index, name: nn, type: src.type }
  const arr = reorderItems.value.slice()
  arr.splice(i + 1, 0, dup)
  reorderItems.value = arr
}

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
.tool-card { user-select: none; }
.card-body { width: 100%; height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; }

.status-unknown { background: #adb5bd; }

/* Add card */
.add-card { color: #0d6efd; border-style: dashed; }
.add-card .plus { font-size: 2rem; line-height: 1; }
.tool-card.disabled { opacity: .5; pointer-events: none; }

/* Modal */
.add-modal-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,0.35); display: flex; align-items: center; justify-content: center; z-index: 1050; }
.add-modal { width: min(520px, 92vw); background: #fff; border-radius: 10px; border: 1px solid #e9ecef; overflow: hidden; }
.reorder-modal { width: 70vw; }
.am-header { padding: 12px; font-weight: 600; border-bottom: 1px solid #e9ecef; background: #f8f9fa; }
.am-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; padding: 12px; }
.am-btn { border: 1px solid #e9ecef; background: #fff; border-radius: 8px; padding: 10px; cursor: pointer; font-weight: 600; }
.am-btn:hover { background: #f8f9fa; }
.am-footer { padding: 10px 12px; border-top: 1px solid #e9ecef; display: flex; justify-content: flex-end; }
.am-close { border: 1px solid #e9ecef; background: #fff; border-radius: 6px; padding: 6px 10px; cursor: pointer; }
.am-apply { border: 1px solid #0d6efd; background: #0d6efd; color: #fff; border-radius: 6px; padding: 6px 10px; cursor: pointer; }

/* Reorder grid */
.re-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 14px; padding: 14px; position: relative; z-index: 1; }
.re-slot {
  width: 100%;
  aspect-ratio: 1 / 1;
  border: 1px solid #e9ecef;
  border-radius: 10px;
  background: #fff;
  position: relative;
  padding: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.slot-badge {
  position: absolute;
  top: 6px; right: 8px;
  font-size: .85rem; color: #495057; background: #f1f3f5;
  border: 1px solid #e9ecef; border-radius: 6px; padding: 2px 6px;
}
.slot-del {
  position: absolute; top: 6px; left: 8px;
  width: 24px; height: 24px; border-radius: 6px;
  background: #fff; border: 1px solid #e9ecef; color: #dc3545;
  line-height: 1; font-size: 18px; display: flex; align-items: center; justify-content: center;
  cursor: pointer; padding: 0;
}
.slot-del:hover { background: #fff5f5; border-color: #f1aeb5; }
.slot-dup {
  position: absolute; top: 6px; left: 38px;
  width: 24px; height: 24px; border-radius: 6px;
  background: #fff; border: 1px solid #e9ecef; color: #0d6efd;
  line-height: 1; font-size: 16px; display: flex; align-items: center; justify-content: center;
  cursor: pointer; padding: 0;
}
.slot-dup:hover { background: #eef5ff; border-color: #cfe2ff; }
.re-tool {
  width: 60%; height: 60%;
  border: 2px dashed #cfe2ff;
  border-radius: 8px;
  background: #f8faff;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  cursor: grab;
  transition: transform .08s ease, box-shadow .12s ease, border-color .15s ease;
  padding: 2px;
  box-sizing: border-box;
}
.re-tool.dragging { opacity: 0; }
.re-tool:hover { border-color: #0d6efd; box-shadow: 0 2px 10px rgba(13,110,253,.12); }
.re-tool:active { cursor: grabbing; transform: scale(.98); }
.re-name { font-weight: 700; color: #0d6efd; text-align: center; padding: 0 2px; font-size: .9rem; line-height: 1.2; word-break: break-word; overflow-wrap: anywhere; }
.re-type { color: #6c757d; text-align: center; font-size: .8rem; line-height: 1.1; margin-top: 2px; padding: 0 2px; word-break: break-word; overflow-wrap: anywhere; }
</style>


