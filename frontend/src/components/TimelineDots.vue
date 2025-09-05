<template>
  <div class="timeline" :style="{ gridTemplateColumns: `repeat(${columns}, 1fr)` }">
    <div
      v-for="(dot, idx) in dots"
      :key="`tl_${idx}`"
      class="timeline-dot"
      :class="{
        'tl-pass': dot === true,
        'tl-fail': dot === false,
        'tl-unknown': dot === null
      }"
    ></div>
  </div>
 </template>

<script setup>
import { defineProps } from 'vue'

const { dots, columns } = defineProps({
  dots: { type: Array, default: () => [] },
  columns: { type: Number, default: 60 }
})
</script>

<style scoped>
.timeline {
  display: grid;
  gap: 4px;
  margin-bottom: 12px;
}
.timeline-dot {
  width: 100%;
  height: 10px;
  border-radius: 2px;
  background: #adb5bd; /* unknown */
}
.timeline-dot.tl-pass { background: #198754; }
.timeline-dot.tl-fail { background: #dc3545; }
.timeline-dot.tl-unknown { background: #adb5bd; }


</style>
