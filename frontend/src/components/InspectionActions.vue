<template>
  <div class="card">
    <div class="card-header">
      <h6 class="mb-0">Ações da Inspeção</h6>
    </div>
    <div class="card-body">
      <div class="d-flex flex-wrap gap-2">
        <button 
          v-for="action in actions" 
          :key="action.key"
          class="btn"
          :class="action.class"
          @click="$emit('action', action.key)"
          :disabled="action.disabled"
        >
          <i :class="action.icon"></i> {{ action.label }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  actions: {
    type: Array,
    default: () => []
  }
})

defineEmits(['action'])
</script>
