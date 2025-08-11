<template>
  <div class="app-container">
    <AppHeader />
    
    <div class="main-content">
      <!-- Lista de inspeções -->
      <div class="card" style="grid-column: span 2;">
        <div class="card-header d-flex justify-content-between align-items-center">
          <h6 class="mb-0">
            <i class="bi bi-list-check text-primary me-2"></i>
            Configurações de Inspeção
          </h6>
          <button class="btn btn-primary btn-sm" @click="createInspection">
            <i class="bi bi-plus-circle"></i> Nova Inspeção
          </button>
        </div>
        <div class="card-body">
          <div class="table-responsive">
            <table class="table table-hover">
              <thead>
                <tr>
                  <th>Nome</th>
                  <th>Status</th>
                  <th>Última Execução</th>
                  <th>Precisão</th>
                  <th>Ações</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="inspection in inspections" :key="inspection.id">
                  <td>
                    <strong>{{ inspection.name }}</strong>
                    <br>
                    <small class="text-muted">{{ inspection.description }}</small>
                  </td>
                  <td>
                    <span class="badge" :class="inspection.statusClass">
                      {{ inspection.status }}
                    </span>
                  </td>
                  <td>{{ inspection.lastRun }}</td>
                  <td>
                    <span class="text-success">{{ inspection.accuracy }}%</span>
                  </td>
                  <td>
                    <div class="btn-group btn-group-sm">
                      <button 
                        class="btn btn-outline-primary" 
                        @click="runInspection(inspection)"
                        :disabled="inspection.status === 'Erro'"
                        :title="inspection.status === 'Erro' ? 'Inspeção com erro' : 'Executar inspeção'"
                      >
                        <i class="bi bi-play"></i>
                      </button>
                      <button 
                        class="btn btn-outline-info" 
                        @click="editInspection(inspection)"
                        title="Editar inspeção"
                      >
                        <i class="bi bi-pencil"></i>
                      </button>
                      <button 
                        class="btn btn-outline-danger" 
                        @click="deleteInspection(inspection)"
                        title="Excluir inspeção"
                      >
                        <i class="bi bi-trash"></i>
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
      
      <!-- Estatísticas -->
      <div class="card">
        <div class="card-header">
          <h6 class="mb-0">
            <i class="bi bi-graph-up text-success me-2"></i>
            Estatísticas
          </h6>
        </div>
        <div class="card-body">
          <div class="text-center">
            <h4 class="text-primary">{{ inspections.length }}</h4>
            <small class="text-muted">Total de Inspeções</small>
          </div>
          <div class="mt-3">
            <div class="d-flex justify-content-between">
              <span>Ativas</span>
              <span class="text-success">{{ activeInspections }}</span>
            </div>
            <div class="d-flex justify-content-between">
              <span>Pausadas</span>
              <span class="text-warning">{{ pausedInspections }}</span>
            </div>
            <div class="d-flex justify-content-between">
              <span>Erro</span>
              <span class="text-danger">{{ errorInspections }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Filtros -->
      <div class="card">
        <div class="card-header">
          <h6 class="mb-0">
            <i class="bi bi-funnel text-info me-2"></i>
            Filtros
          </h6>
        </div>
        <div class="card-body">
          <div class="mb-3">
            <label class="form-label">Status</label>
            <select class="form-select form-select-sm">
              <option value="">Todos</option>
              <option value="active">Ativas</option>
              <option value="paused">Pausadas</option>
              <option value="error">Com Erro</option>
            </select>
          </div>
          <div class="mb-3">
            <label class="form-label">Precisão</label>
            <select class="form-select form-select-sm">
              <option value="">Qualquer</option>
              <option value="high">Alta (&gt;90%)</option>
              <option value="medium">Média (70-90%)</option>
              <option value="low">Baixa (&lt;70%)</option>
            </select>
          </div>
          <button class="btn btn-outline-primary btn-sm w-100">
            <i class="bi bi-search"></i> Aplicar Filtros
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import AppHeader from '@/components/AppHeader.vue'

const router = useRouter()

// Dados mock para demonstração
const inspections = ref([
  {
    id: 1,
    name: 'Inspeção de Qualidade',
    description: 'Detecção de defeitos em produtos',
    status: 'Ativo',
    statusClass: 'bg-success',
    lastRun: '2024-01-15 14:30',
    accuracy: 95
  },
  {
    id: 2,
    name: 'Detecção de Defeitos',
    description: 'Análise de qualidade automática',
    status: 'Parado',
    statusClass: 'bg-warning',
    lastRun: '2024-01-14 09:15',
    accuracy: 87
  },
  {
    id: 3,
    name: 'Contagem de Objetos',
    description: 'Contagem automática de peças',
    status: 'Erro',
    statusClass: 'bg-danger',
    lastRun: '2024-01-13 16:45',
    accuracy: 0
  }
])

// Estatísticas calculadas
const activeInspections = computed(() => 
  inspections.value.filter(i => i.status === 'Ativo').length
)

const pausedInspections = computed(() => 
  inspections.value.filter(i => i.status === 'Parado').length
)

const errorInspections = computed(() => 
  inspections.value.filter(i => i.status === 'Erro').length
)

// Funções de ação
function createInspection() {
  router.push('/inspection/edit')
}

function runInspection(inspection) {
  console.log('Executar inspeção:', inspection.name)
  // TODO: Implementar execução da inspeção
  // Redirecionar para LiveView ou executar via API
  router.push('/live')
}

function editInspection(inspection) {
  router.push(`/inspection/edit/${inspection.id}`)
}

function deleteInspection(inspection) {
  if (confirm(`Tem certeza que deseja excluir "${inspection.name}"?`)) {
    console.log('Excluir inspeção:', inspection.name)
    // TODO: Implementar exclusão via API
    const index = inspections.value.findIndex(i => i.id === inspection.id)
    if (index > -1) {
      inspections.value.splice(index, 1)
    }
  }
}
</script>
