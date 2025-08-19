<template>
  <img 
    :src="iconPath" 
    :alt="`${name} icon`"
    :class="iconClass"
    :style="iconStyle"
  />
</template>

<script setup>
import { computed } from 'vue'
import { getImagePath } from '@/utils/imageRouter'

const props = defineProps({
  name: {
    type: String,
    required: true
  },
  size: {
    type: String,
    default: '1em'
  },
  color: {
    type: String,
    default: 'currentColor'
  },
  class: {
    type: String,
    default: ''
  }
})

const iconPath = computed(() => {
  return getImagePath(`icons/${props.name}.svg`)
})

const iconClass = computed(() => {
  return `icon icon-${props.name} ${props.class}`.trim()
})

const iconStyle = computed(() => {
  return {
    width: props.size,
    height: props.size,
    filter: props.color !== 'currentColor' ? `brightness(0) saturate(100%) invert(1) hue-rotate(${getHueFromColor(props.color)})` : 'none'
  }
})

function getHueFromColor(color) {
  // Função simples para converter cores para hue-rotate
  const colorMap = {
    'primary': '210deg',
    'secondary': '220deg',
    'success': '120deg',
    'danger': '0deg',
    'warning': '45deg',
    'info': '180deg',
    'light': '0deg',
    'dark': '0deg'
  }
  return colorMap[color] || '0deg'
}
</script>

<style scoped>
.icon {
  display: inline-block;
  vertical-align: text-bottom;
  line-height: 1;
}
</style>
