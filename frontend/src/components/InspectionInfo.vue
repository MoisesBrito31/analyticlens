<template>
  <div class="card">
    <div class="card-header">
      <h6 class="mb-0">Informações da Inspeção</h6>
    </div>
    <div class="card-body">
      <div class="row">
        <div class="col-md-6">
          <div class="mb-2">
            <strong>Nome:</strong> {{ inspection.name || 'N/A' }}
          </div>
          <div class="mb-2">
            <strong>Status:</strong>
            <span class="badge" :class="statusBadgeClass">
              {{ inspection.status || 'N/A' }}
            </span>
          </div>
        </div>
        <div class="col-md-6">
          <div class="mb-2">
            <strong>Frame:</strong> {{ inspection.frame || 'N/A' }}
          </div>
          <div class="mb-2">
            <strong>Status Geral:</strong>
            <span class="badge" :class="generalStatusBadgeClass">
              {{ inspection.generalStatus || 'N/A' }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  inspection: {
    type: Object,
    default: () => ({
      name: '',
      status: '',
      frame: '',
      generalStatus: ''
    })
  }
})

const statusBadgeClass = computed(() => {
  const status = props.inspection.status?.toLowerCase()
  if (status === 'aprovada') return 'bg-success'
  if (status === 'reprovada') return 'bg-danger'
  return 'bg-secondary'
})

const generalStatusBadgeClass = computed(() => {
  const status = props.inspection.generalStatus?.toLowerCase()
  if (status === 'ativo') return 'bg-success'
  if (status === 'parado') return 'bg-warning'
  return 'bg-secondary'
})
</script>
