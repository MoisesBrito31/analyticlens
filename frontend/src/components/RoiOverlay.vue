<template>
  <svg ref="svgEl" class="contour-svg" :viewBox="viewBox" preserveAspectRatio="xMidYMid meet" :style="{ pointerEvents: editable ? 'all' : 'none' }">
    <!-- ROI retângulo -->
    <rect v-if="showRectOverlay"
      :x="drawRect?.x || 0" :y="drawRect?.y || 0"
      :width="drawRect?.w || 0" :height="drawRect?.h || 0"
      fill="rgba(13,110,253,0.15)" stroke="#0d6efd" stroke-width="2" vector-effect="non-scaling-stroke"
      :pointer-events="editable ? 'all' : 'none'"
      @mousedown.stop.prevent="editable ? onRectDown($event) : null"
    />

    <!-- Handles do retângulo -->
    <template v-if="editable && showRectOverlay && drawRect">
      <rect v-for="(h, i) in rectHandles" :key="`rh_${i}`"
        :x="h.x - handleSize/2" :y="h.y - handleSize/2" :width="handleSize" :height="handleSize"
        fill="#0d6efd" opacity="0.9" vector-effect="non-scaling-stroke" pointer-events="all"
        @mousedown.stop.prevent="onRectHandleDown($event, h.pos)"
      />
    </template>

    <!-- ROI círculo -->
    <circle v-if="showCircleOverlay" :cx="drawCircle.cx" :cy="drawCircle.cy" :r="drawCircle.r"
      fill="rgba(13,110,253,0.15)" stroke="#0d6efd" stroke-width="2" vector-effect="non-scaling-stroke"
      :pointer-events="editable ? 'all' : 'none'"
      @mousedown.stop.prevent="editable ? onCircleDown($event) : null"
    />
    <!-- Handle de raio do círculo -->
    <template v-if="editable && showCircleOverlay">
      <circle :cx="drawCircle.cx + drawCircle.r" :cy="drawCircle.cy" :r="handleSize/2"
        fill="#0d6efd" opacity="0.9" vector-effect="non-scaling-stroke" pointer-events="all"
        @mousedown.stop.prevent="onCircleRadiusDown($event)"
      />
    </template>

    <!-- ROI elipse -->
    <g v-if="showEllipseOverlay" :transform="`rotate(${drawEllipse.angle} ${drawEllipse.cx} ${drawEllipse.cy})`">
      <ellipse :cx="drawEllipse.cx" :cy="drawEllipse.cy" :rx="drawEllipse.rx" :ry="drawEllipse.ry"
        fill="rgba(13,110,253,0.15)" stroke="#0d6efd" stroke-width="2" vector-effect="non-scaling-stroke"
        :pointer-events="editable ? 'all' : 'none'"
        @mousedown.stop.prevent="editable ? onEllipseDown($event) : null"
      />
      <!-- Handles simples (sem rotação) para rx/ry quando angle == 0 -->
      <template v-if="editable && drawEllipse.angle === 0">
        <circle :cx="drawEllipse.cx + drawEllipse.rx" :cy="drawEllipse.cy" :r="handleSize/2"
          fill="#0d6efd" opacity="0.9" pointer-events="all" @mousedown.stop.prevent="onEllipseRxDown($event)" />
        <circle :cx="drawEllipse.cx" :cy="drawEllipse.cy + drawEllipse.ry" :r="handleSize/2"
          fill="#0d6efd" opacity="0.9" pointer-events="all" @mousedown.stop.prevent="onEllipseRyDown($event)" />
      </template>
    </g>

    <!-- Blobs: centróides -->
    <g v-if="showBlobCentroids">
      <g v-for="(pt, i) in blobCentroidPointsPx" :key="`bc_${i}`" :stroke="analysisColors.strokeStrong" stroke-width="2" vector-effect="non-scaling-stroke">
        <line :x1="pt.x - 6" :y1="pt.y" :x2="pt.x + 6" :y2="pt.y" />
        <line :x1="pt.x" :y1="pt.y - 6" :x2="pt.x" :y2="pt.y + 6" />
      </g>
    </g>

    <!-- Blobs: caixas -->
    <g v-if="showBlobBoxes">
      <rect v-for="(bb, i) in blobBoxesPx" :key="`bb_${i}`" :x="bb.x" :y="bb.y" :width="bb.w" :height="bb.h"
        fill="none" :stroke="analysisColors.strokeMed" stroke-width="2" vector-effect="non-scaling-stroke" />
    </g>

    <!-- Blobs: contornos -->
    <g v-if="showBlobContours && hasContours">
      <template v-for="(path, i) in contourPaths" :key="`cp_${i}`">
        <!-- Preenchimento com regra evenodd para manter buracos vazios -->
        <path :d="path" fill-rule="evenodd" :fill="analysisColors.fillContour" :stroke="analysisColors.strokeMed" stroke-width="1.0" vector-effect="non-scaling-stroke" stroke-linejoin="round" stroke-linecap="round" shape-rendering="geometricPrecision" />
      </template>
    </g>
  </svg>
</template>

<script setup>
import { defineProps, defineEmits, ref, computed, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps({
  viewBox: { type: String, required: true },
  showRectOverlay: { type: Boolean, default: false },
  effectiveRoiRect: { type: Object, default: null },
  showCircleOverlay: { type: Boolean, default: false },
  roiCircle: { type: Object, default: () => ({ cx: 0, cy: 0, r: 0 }) },
  showEllipseOverlay: { type: Boolean, default: false },
  roiEllipse: { type: Object, default: () => ({ cx: 0, cy: 0, rx: 0, ry: 0, angle: 0 }) },
  showBlobCentroids: { type: Boolean, default: false },
  blobCentroidPointsPx: { type: Array, default: () => [] },
  showBlobBoxes: { type: Boolean, default: false },
  blobBoxesPx: { type: Array, default: () => [] },
  showBlobContours: { type: Boolean, default: false },
  contourPaths: { type: Array, default: () => [] },
  hasContours: { type: Boolean, default: false },
  analysisColors: { type: Object, default: () => ({ strokeStrong: '#198754', strokeMed: '#198754', fillContour: 'rgba(25, 135, 84, 0.25)' }) },
  // Novos props para edição interativa
  editable: { type: Boolean, default: false },
  roiShape: { type: Object, default: null },
  // Controle de sensibilidade e snapping
  dragGain: { type: Number, default: 1 },
  snapToGrid: { type: Boolean, default: false },
  gridStep: { type: Number, default: 1 }
})

const emit = defineEmits(['roi-change'])

const svgEl = ref(null)
const handleSize = 8

function parseViewBox(vbStr) {
  const parts = String(vbStr || '').trim().split(/\s+/).map(parseFloat)
  const [minX = 0, minY = 0, w = 0, h = 0] = parts
  return { minX, minY, w, h }
}

function clientToSvg(evt) {
  const svg = svgEl.value
  if (!svg) return { x: 0, y: 0 }
  const rect = svg.getBoundingClientRect()
  const vb = parseViewBox(props.viewBox)
  // Considerar letterboxing por preserveAspectRatio="xMidYMid meet"
  const scale = Math.min(rect.width / vb.w, rect.height / vb.h) || 1
  const drawW = vb.w * scale
  const drawH = vb.h * scale
  const offX = (rect.width - drawW) / 2
  const offY = (rect.height - drawH) / 2
  const localX = Math.max(0, Math.min(drawW, evt.clientX - rect.left - offX))
  const localY = Math.max(0, Math.min(drawH, evt.clientY - rect.top - offY))
  const x = vb.minX + localX / scale
  const y = vb.minY + localY / scale
  return { x, y }
}

const drag = ref({ active: false, mode: '', startX: 0, startY: 0, init: null, current: null, modGain: 1 })

const drawRect = computed(() => {
  if (drag.value.active && drag.value.mode.startsWith('rect') && drag.value.current?.rect) return drag.value.current.rect
  return props.effectiveRoiRect
})

const drawCircle = computed(() => {
  if (drag.value.active && drag.value.mode.startsWith('circle') && drag.value.current?.circle) return drag.value.current.circle
  return props.roiCircle
})

const drawEllipse = computed(() => {
  if (drag.value.active && drag.value.mode.startsWith('ellipse') && drag.value.current?.ellipse) return drag.value.current.ellipse
  return props.roiEllipse
})

const rectHandles = computed(() => {
  const r = drawRect.value
  if (!r) return []
  const x = r.x, y = r.y, w = r.w, h = r.h
  return [
    { x, y, pos: 'tl' },
    { x: x + w, y, pos: 'tr' },
    { x, y: y + h, pos: 'bl' },
    { x: x + w, y: y + h, pos: 'br' }
  ]
})

function clampRect(vb, r, minSize = 4) {
  let x = Math.max(vb.minX, Math.min(r.x, vb.minX + vb.w - minSize))
  let y = Math.max(vb.minY, Math.min(r.y, vb.minY + vb.h - minSize))
  let w = Math.max(minSize, Math.min(r.w, vb.minX + vb.w - x))
  let h = Math.max(minSize, Math.min(r.h, vb.minY + vb.h - y))
  return { x, y, w, h }
}

function onRectDown(evt) {
  if (!props.editable || !drawRect.value) return
  const p = clientToSvg(evt)
  const mod = evt.shiftKey ? 0.25 : 1
  const base = { ...drawRect.value }
  drag.value = { active: true, mode: 'rect-move', startX: p.x, startY: p.y, init: { rect: base }, current: { rect: base }, modGain: mod }
  window.addEventListener('mousemove', onMouseMove)
  window.addEventListener('mouseup', onMouseUp)
}

function onRectHandleDown(evt, pos) {
  if (!props.editable || !drawRect.value) return
  const p = clientToSvg(evt)
  const mod = evt.shiftKey ? 0.25 : 1
  const base = { ...drawRect.value }
  drag.value = { active: true, mode: `rect-resize-${pos}`, startX: p.x, startY: p.y, init: { rect: base }, current: { rect: base }, modGain: mod }
  window.addEventListener('mousemove', onMouseMove)
  window.addEventListener('mouseup', onMouseUp)
}

function onCircleDown(evt) {
  if (!props.editable) return
  const p = clientToSvg(evt)
  const mod = evt.shiftKey ? 0.25 : 1
  const base = { ...props.roiCircle }
  drag.value = { active: true, mode: 'circle-move', startX: p.x, startY: p.y, init: { circle: base }, current: { circle: base }, modGain: mod }
  window.addEventListener('mousemove', onMouseMove)
  window.addEventListener('mouseup', onMouseUp)
}

function onCircleRadiusDown(evt) {
  if (!props.editable) return
  const p = clientToSvg(evt)
  const mod = evt.shiftKey ? 0.25 : 1
  const base = { ...props.roiCircle }
  drag.value = { active: true, mode: 'circle-resize', startX: p.x, startY: p.y, init: { circle: base }, current: { circle: base }, modGain: mod }
  window.addEventListener('mousemove', onMouseMove)
  window.addEventListener('mouseup', onMouseUp)
}

function onEllipseDown(evt) {
  if (!props.editable) return
  const p = clientToSvg(evt)
  const mod = evt.shiftKey ? 0.25 : 1
  const base = { ...props.roiEllipse }
  drag.value = { active: true, mode: 'ellipse-move', startX: p.x, startY: p.y, init: { ellipse: base }, current: { ellipse: base }, modGain: mod }
  window.addEventListener('mousemove', onMouseMove)
  window.addEventListener('mouseup', onMouseUp)
}

function onEllipseRxDown(evt) {
  if (!props.editable) return
  const p = clientToSvg(evt)
  const mod = evt.shiftKey ? 0.25 : 1
  const base = { ...props.roiEllipse }
  drag.value = { active: true, mode: 'ellipse-resize-rx', startX: p.x, startY: p.y, init: { ellipse: base }, current: { ellipse: base }, modGain: mod }
  window.addEventListener('mousemove', onMouseMove)
  window.addEventListener('mouseup', onMouseUp)
}

function onEllipseRyDown(evt) {
  if (!props.editable) return
  const p = clientToSvg(evt)
  const mod = evt.shiftKey ? 0.25 : 1
  const base = { ...props.roiEllipse }
  drag.value = { active: true, mode: 'ellipse-resize-ry', startX: p.x, startY: p.y, init: { ellipse: base }, current: { ellipse: base }, modGain: mod }
  window.addEventListener('mousemove', onMouseMove)
  window.addEventListener('mouseup', onMouseUp)
}

function onMouseMove(evt) {
  if (!drag.value.active) return
  const vb = parseViewBox(props.viewBox)
  const p = clientToSvg(evt)
  const gain = props.dragGain * (drag.value.modGain || 1)
  const dx = (p.x - drag.value.startX) * gain
  const dy = (p.y - drag.value.startY) * gain
  const mode = drag.value.mode
  const snap = (val) => props.snapToGrid && props.gridStep > 0 ? Math.round(val / props.gridStep) * props.gridStep : val
  if (mode.startsWith('rect')) {
    const r0 = drag.value.init.rect
    let r = { ...r0 }
    if (mode === 'rect-move') {
      r.x = r0.x + dx
      r.y = r0.y + dy
    } else if (mode === 'rect-resize-tl') {
      r.x = r0.x + dx; r.y = r0.y + dy; r.w = r0.w - dx; r.h = r0.h - dy
    } else if (mode === 'rect-resize-tr') {
      r.y = r0.y + dy; r.w = r0.w + dx; r.h = r0.h - dy
    } else if (mode === 'rect-resize-bl') {
      r.x = r0.x + dx; r.w = r0.w - dx; r.h = r0.h + dy
    } else if (mode === 'rect-resize-br') {
      r.w = r0.w + dx; r.h = r0.h + dy
    }
    r = clampRect(vb, r)
    r = { x: snap(r.x), y: snap(r.y), w: Math.max(2, snap(r.w)), h: Math.max(2, snap(r.h)) }
    drag.value.current = { ...(drag.value.current || {}), rect: r }
  } else if (mode.startsWith('circle')) {
    const c0 = drag.value.init.circle
    let c = { ...c0 }
    if (mode === 'circle-move') {
      c.cx = c0.cx + dx
      c.cy = c0.cy + dy
      // limitar para não sair muito da viewbox (raio preserva)
      const minX = vb.minX + c.r
      const maxX = vb.minX + vb.w - c.r
      const minY = vb.minY + c.r
      const maxY = vb.minY + vb.h - c.r
      c.cx = snap(Math.max(minX, Math.min(c.cx, maxX)))
      c.cy = snap(Math.max(minY, Math.min(c.cy, maxY)))
    } else if (mode === 'circle-resize') {
      const nx = p.x - c0.cx
      const ny = p.y - c0.cy
      const desired = Math.max(2, Math.hypot(nx, ny))
      const deltaR = (desired - c0.r) * gain
      const r = c0.r + deltaR
      const rMax = Math.min(c0.cx - vb.minX, vb.minX + vb.w - c0.cx, c0.cy - vb.minY, vb.minY + vb.h - c0.cy)
      c.r = snap(Math.max(2, Math.min(r, rMax)))
    }
    drag.value.current = { ...(drag.value.current || {}), circle: c }
  } else if (mode.startsWith('ellipse')) {
    const e0 = drag.value.init.ellipse
    let e = { ...e0 }
    if (mode === 'ellipse-move') {
      e.cx = e0.cx + dx
      e.cy = e0.cy + dy
      e.cx = snap(Math.max(vb.minX + e.rx, Math.min(e.cx, vb.minX + vb.w - e.rx)))
      e.cy = snap(Math.max(vb.minY + e.ry, Math.min(e.cy, vb.minY + vb.h - e.ry)))
    } else if (mode === 'ellipse-resize-rx') {
      e.rx = Math.max(2, e0.rx + dx)
      e.rx = Math.min(e.rx, Math.min(e.cx - vb.minX, vb.minX + vb.w - e.cx))
      e.rx = snap(e.rx)
    } else if (mode === 'ellipse-resize-ry') {
      e.ry = Math.max(2, e0.ry + dy)
      e.ry = Math.min(e.ry, Math.min(e.cy - vb.minY, vb.minY + vb.h - e.cy))
      e.ry = snap(e.ry)
    }
    drag.value.current = { ...(drag.value.current || {}), ellipse: e }
  }
}

function onMouseUp() {
  if (!drag.value.active) return
  const mode = drag.value.mode
  const init = drag.value.init
  const current = drag.value.current
  drag.value.active = false
  window.removeEventListener('mousemove', onMouseMove)
  window.removeEventListener('mouseup', onMouseUp)
  if (mode.startsWith('rect') && (current?.rect || init?.rect)) {
    const r = current?.rect || init?.rect
    emit('roi-change', { shape: 'rect', rect: { ...r } })
  } else if (mode.startsWith('circle') && (current?.circle || init?.circle)) {
    const c = current?.circle || init?.circle
    emit('roi-change', { shape: 'circle', circle: { ...c } })
  } else if (mode.startsWith('ellipse') && (current?.ellipse || init?.ellipse)) {
    const e = current?.ellipse || init?.ellipse
    emit('roi-change', { shape: 'ellipse', ellipse: { ...e } })
  }
  drag.value.current = null
}

onMounted(() => {
  // Garantia: removemos listeners em caso de desmontagem no meio do drag
  window.addEventListener('mouseup', onMouseUp)
})

onBeforeUnmount(() => {
  window.removeEventListener('mousemove', onMouseMove)
  window.removeEventListener('mouseup', onMouseUp)
})
</script>

<style scoped>
.contour-svg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}
</style>
