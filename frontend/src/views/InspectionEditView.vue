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
          :actions="editActions" 
          @action="handleAction" 
        />
      </div>
      
      <!-- Canvas para edição de tools -->
      <div class="tools-canvas">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h6 class="mb-0">
              <i class="bi bi-diagram-3 text-primary me-2"></i>
              Canvas de Tools
            </h6>
            <div class="btn-group btn-group-sm">
              <button 
                class="btn btn-outline-primary" 
                @click="addTool"
                :disabled="!hasSelection"
              >
                <i class="bi bi-plus-circle"></i> Adicionar
              </button>
              <button 
                class="btn btn-outline-danger" 
                @click="removeSelected"
                :disabled="!hasSelection"
              >
                <i class="bi bi-trash"></i> Remover
              </button>
            </div>
          </div>
          <div class="card-body">
            <div class="text-center py-5">
              <i class="bi bi-diagram-3 text-muted" style="font-size: 3rem;"></i>
              <p class="text-muted mt-3">Canvas será implementado aqui</p>
              <p class="text-muted small">Vue Flow para pipeline visual</p>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Propriedades da tool selecionada -->
      <div class="tool-properties">
        <div class="card">
          <div class="card-header">
            <h6 class="mb-0">
              <i class="bi bi-gear text-info me-2"></i>
              Propriedades da Tool
            </h6>
          </div>
          <div class="card-body">
            <div v-if="selectedTool" class="text-center py-3">
              <h6 class="text-primary">{{ selectedTool.name }}</h6>
              <p class="text-muted small">{{ selectedTool.description }}</p>
              <div class="mt-3">
                <button class="btn btn-primary btn-sm">
                  <i class="bi bi-pencil"></i> Editar
                </button>
              </div>
            </div>
            <div v-else class="text-center py-5">
              <i class="bi bi-gear text-muted" style="font-size: 2rem;"></i>
              <p class="text-muted mt-3">Selecione uma tool</p>
              <p class="text-muted small">para ver suas propriedades</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppHeader from '@/components/AppHeader.vue'
import LastInspectedImage from '@/components/LastInspectedImage.vue'
import InspectionInfo from '@/components/InspectionInfo.vue'
import InspectionActions from '@/components/InspectionActions.vue'

const route = useRoute()
const router = useRouter()

// Detectar se está editando ou criando
const isEditing = computed(() => !!route.params.id)
const inspectionId = computed(() => route.params.id)

// Dados mock para demonstração
const lastImage = ref({
  url: '',
  name: 'Nenhuma imagem'
})

const currentInspection = ref({
  name: 'Nova Inspeção',
  status: 'Em edição',
  frame: 'Frame atual',
  generalStatus: 'Parado'
})

const editActions = ref([
  { key: 'save', label: 'Salvar', icon: 'bi bi-save', class: 'btn-success' },
  { key: 'load', label: 'Carregar', icon: 'bi bi-folder-open', class: 'btn-primary' },
  { key: 'trigger', label: 'Trigger', icon: 'bi bi-lightning', class: 'btn-warning' },
  { key: 'discard', label: 'Descartar', icon: 'bi bi-x-circle', class: 'btn-danger' }
])

const selectedTool = ref(null)
const hasSelection = computed(() => !!selectedTool.value)

// Carregar dados da inspeção se estiver editando
onMounted(async () => {
  if (isEditing.value) {
    await loadInspection(inspectionId.value)
  }
})

async function loadInspection(id) {
  console.log('Carregando inspeção:', id)
  // TODO: Implementar carregamento via API
  // Por enquanto, simular dados
  currentInspection.value = {
    name: `Inspeção ${id}`,
    status: 'Em edição',
    frame: 'Frame atual',
    generalStatus: 'Parado'
  }
}

function handleImageClick() {
  console.log('Imagem clicada - futura implementação')
}

function handleAction(actionKey) {
  console.log('Ação executada:', actionKey)
  
  switch (actionKey) {
    case 'save':
      saveInspection()
      break
    case 'load':
      // TODO: Implementar carregamento
      console.log('Carregar inspeção')
      break
    case 'trigger':
      // TODO: Implementar trigger
      console.log('Trigger inspeção')
      break
    case 'discard':
      if (confirm('Tem certeza que deseja descartar as alterações?')) {
        router.back()
      }
      break
  }
}

async function saveInspection() {
  console.log('Salvando inspeção...')
  // TODO: Implementar salvamento via API
  if (isEditing.value) {
    console.log('Atualizando inspeção existente:', inspectionId.value)
  } else {
    console.log('Criando nova inspeção')
  }
  
  // Simular sucesso
  alert('Inspeção salva com sucesso!')
  router.push('/inspections')
}

function addTool() {
  console.log('Adicionar tool - futura implementação')
}

function removeSelected() {
  console.log('Remover tool selecionada - futura implementação')
  selectedTool.value = null
}
</script>
