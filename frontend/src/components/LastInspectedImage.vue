<template>
  <div class="card">
    <div class="card-header">
      <h6 class="mb-0">Última Imagem Inspecionada</h6>
    </div>
    <div class="card-body text-center">
      <div v-if="imageUrl" class="mb-3">
        <img 
          :src="imageUrl" 
          :alt="imageName"
          class="img-fluid rounded"
          style="max-height: 200px; cursor: pointer;"
          @click="$emit('imageClick')"
        />
        <div class="mt-2">
          <small class="text-muted">{{ imageName }}</small>
        </div>
      </div>
      <div v-else class="text-muted">
        <i class="bi bi-image" style="font-size: 3rem;"></i>
        <p class="mt-2">Nenhuma imagem inspecionada</p>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  imageUrl: {
    type: String,
    default: ''
  },
  imageName: {
    type: String,
    default: 'Imagem'
  }
})

defineEmits(['imageClick'])
</script>
