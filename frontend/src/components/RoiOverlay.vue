<template>
  <svg class="contour-svg" :viewBox="viewBox" preserveAspectRatio="xMidYMid meet">
    <!-- ROI retângulo -->
    <rect v-if="showRectOverlay"
      :x="effectiveRoiRect?.x || 0" :y="effectiveRoiRect?.y || 0"
      :width="effectiveRoiRect?.w || 0" :height="effectiveRoiRect?.h || 0"
      fill="rgba(13,110,253,0.15)" stroke="#0d6efd" stroke-width="2" vector-effect="non-scaling-stroke" />

    <!-- ROI círculo -->
    <circle v-if="showCircleOverlay" :cx="roiCircle.cx" :cy="roiCircle.cy" :r="roiCircle.r"
      fill="rgba(13,110,253,0.15)" stroke="#0d6efd" stroke-width="2" vector-effect="non-scaling-stroke" />

    <!-- ROI elipse -->
    <g v-if="showEllipseOverlay" :transform="`rotate(${roiEllipse.angle} ${roiEllipse.cx} ${roiEllipse.cy})`">
      <ellipse :cx="roiEllipse.cx" :cy="roiEllipse.cy" :rx="roiEllipse.rx" :ry="roiEllipse.ry"
        fill="rgba(13,110,253,0.15)" stroke="#0d6efd" stroke-width="2" vector-effect="non-scaling-stroke" />
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
        <path :d="path" :fill="analysisColors.fillContour" :stroke="analysisColors.fillContour" stroke-width="0.8" vector-effect="non-scaling-stroke" stroke-linejoin="round" stroke-linecap="round" shape-rendering="geometricPrecision" />
      </template>
    </g>
  </svg>
</template>

<script setup>
import { defineProps } from 'vue'

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
  analysisColors: { type: Object, default: () => ({ strokeStrong: '#198754', strokeMed: '#198754', fillContour: 'rgba(25, 135, 84, 0.25)' }) }
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
