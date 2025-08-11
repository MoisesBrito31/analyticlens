<template>
  <div class="app-container">
    <AppHeader />
    
    <div class="main-content">
      <!-- Imagem da última inspeção -->
      <div class="last-image">
        <LastInspectedImage 
          :image="lastImage" 
          @image-click="handleImageClick" 
        />
      </div>
      
      <!-- Informações da inspeção -->
      <div class="inspection-info">
        <InspectionInfo :inspection="currentInspection" />
      </div>
      
      <!-- Ações da inspeção -->
      <div class="inspection-actions">
        <InspectionActions 
          :actions="liveActions" 
          @action="handleAction" 
        />
      </div>
      
      <!-- Área de streaming ao vivo -->
      <div class="live-stream">
        <div class="card">
          <div class="card-header">
            <h6 class="mb-0">
              <i class="bi bi-camera-video-fill text-primary me-2"></i>
              Streaming ao Vivo
            </h6>
          </div>
          <div class="card-body">
            <div class="text-center py-5">
              <i class="bi bi-camera-video text-muted" style="font-size: 3rem;"></i>
              <p class="text-muted mt-3">Streaming será implementado aqui</p>
              <p class="text-muted small">Integração com câmeras IP/RTSP</p>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Métricas em tempo real -->
      <div class="card">
        <div class="card-header">
          <h6 class="mb-0">
            <i class="bi bi-graph-up text-success me-2"></i>
            Métricas em Tempo Real
          </h6>
        </div>
        <div class="card-body">
          <div class="row text-center">
            <div class="col-6">
              <h4 class="text-primary">24</h4>
              <small class="text-muted">FPS</small>
            </div>
            <div class="col-6">
              <h4 class="text-success">98.5%</h4>
              <small class="text-muted">Precisão</small>
            </div>
          </div>
          <div class="row text-center mt-3">
            <div class="col-6">
              <h4 class="text-warning">12ms</h4>
              <small class="text-muted">Latência</small>
            </div>
            <div class="col-6">
              <h4 class="text-info">156</h4>
              <small class="text-muted">Total Inspeções</small>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import AppHeader from '@/components/AppHeader.vue'
import LastInspectedImage from '@/components/LastInspectedImage.vue'
import InspectionInfo from '@/components/InspectionInfo.vue'
import InspectionActions from '@/components/InspectionActions.vue'

// Dados mock para demonstração
const lastImage = ref({
  url: '',
  name: 'Nenhuma imagem'
})

const currentInspection = ref({
  name: 'Inspeção Padrão',
  status: 'Ativo',
  frame: 'Frame 001',
  generalStatus: 'Ativo'
})

const liveActions = ref([
  { key: 'run', label: 'Rodar', icon: 'bi bi-play-fill', class: 'btn-success' },
  { key: 'stop', label: 'Parar', icon: 'bi bi-stop-fill', class: 'btn-warning' },
  { key: 'select', label: 'Selecionar', icon: 'bi bi-check2-square', class: 'btn-primary' },
  { key: 'edit', label: 'Editar', icon: 'bi bi-pencil', class: 'btn-info' },
  { key: 'create', label: 'Criar', icon: 'bi bi-plus-circle', class: 'btn-primary' }
])

function handleImageClick() {
  console.log('Imagem clicada - futura implementação')
}

function handleAction(actionKey) {
  console.log('Ação executada:', actionKey)
  // Implementação futura das ações
}
</script>
