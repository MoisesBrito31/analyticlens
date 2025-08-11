<template>
  <div class="app-container">
    <AppHeader />
    
    <div class="main-content">
      <!-- Log de imagens -->
      <div class="card" style="grid-column: span 2;">
        <div class="card-header">
          <h6 class="mb-0">
            <i class="bi bi-images text-primary me-2"></i>
            Histórico de Imagens Inspecionadas
          </h6>
        </div>
        <div class="card-body">
          <div class="table-responsive">
            <table class="table table-hover">
              <thead>
                <tr>
                  <th>Imagem</th>
                  <th>Inspeção</th>
                  <th>Status</th>
                  <th>Data/Hora</th>
                  <th>Precisão</th>
                  <th>Ações</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="log in imageLogs" :key="log.id">
                  <td>
                    <div class="d-flex align-items-center">
                      <img 
                        :src="log.thumbnail" 
                        :alt="log.filename"
                        class="rounded me-2"
                        style="width: 50px; height: 50px; object-fit: cover;"
                      />
                      <div>
                        <strong>{{ log.filename }}</strong>
                        <br>
                        <small class="text-muted">{{ log.size }}</small>
                      </div>
                    </div>
                  </td>
                  <td>{{ log.inspectionName }}</td>
                  <td>
                    <span class="badge" :class="log.statusClass">
                      {{ log.status }}
                    </span>
                  </td>
                  <td>{{ log.timestamp }}</td>
                  <td>
                    <span class="text-success">{{ log.accuracy }}%</span>
                  </td>
                  <td>
                    <div class="btn-group btn-group-sm">
                      <button class="btn btn-outline-primary">
                        <i class="bi bi-eye"></i>
                      </button>
                      <button class="btn btn-outline-info">
                        <i class="bi bi-download"></i>
                      </button>
                      <button class="btn btn-outline-danger">
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
            <label class="form-label">Data</label>
            <input type="date" class="form-control form-control-sm">
          </div>
          <div class="mb-3">
            <label class="form-label">Status</label>
            <select class="form-select form-select-sm">
              <option value="">Todos</option>
              <option value="pass">Aprovado</option>
              <option value="fail">Reprovado</option>
              <option value="error">Erro</option>
            </select>
          </div>
          <div class="mb-3">
            <label class="form-label">Inspeção</label>
            <select class="form-select form-select-sm">
              <option value="">Todas</option>
              <option value="blob">Blob Detection</option>
              <option value="edge">Edge Detection</option>
              <option value="match">Template Matching</option>
            </select>
          </div>
          <button class="btn btn-outline-primary btn-sm w-100">
            <i class="bi bi-search"></i> Aplicar Filtros
          </button>
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
            <h4 class="text-primary">{{ imageLogs.length }}</h4>
            <small class="text-muted">Total de Imagens</small>
          </div>
          <div class="mt-3">
            <div class="d-flex justify-content-between">
              <span>Aprovadas</span>
              <span class="text-success">{{ approvedImages }}</span>
            </div>
            <div class="d-flex justify-content-between">
              <span>Reprovadas</span>
              <span class="text-danger">{{ rejectedImages }}</span>
            </div>
            <div class="d-flex justify-content-between">
              <span>Com Erro</span>
              <span class="text-warning">{{ errorImages }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import AppHeader from '@/components/AppHeader.vue'

// Dados mock para demonstração
const imageLogs = ref([
  {
    id: 1,
    filename: 'produto_001.jpg',
    thumbnail: 'https://via.placeholder.com/50x50/007bff/ffffff?text=P1',
    size: '2.3 MB',
    inspectionName: 'Detecção de Defeitos',
    status: 'Aprovado',
    statusClass: 'bg-success',
    timestamp: '2024-01-15 14:30:22',
    accuracy: 98
  },
  {
    id: 2,
    filename: 'produto_002.jpg',
    thumbnail: 'https://via.placeholder.com/50x50/dc3545/ffffff?text=P2',
    size: '1.8 MB',
    inspectionName: 'Contagem de Objetos',
    status: 'Reprovado',
    statusClass: 'bg-danger',
    timestamp: '2024-01-15 14:28:15',
    accuracy: 45
  },
  {
    id: 3,
    filename: 'produto_003.jpg',
    thumbnail: 'https://via.placeholder.com/50x50/ffc107/ffffff?text=P3',
    size: '2.1 MB',
    inspectionName: 'Inspeção de Qualidade',
    status: 'Erro',
    statusClass: 'bg-warning',
    timestamp: '2024-01-15 14:25:08',
    accuracy: 0
  }
])

// Estatísticas calculadas
const approvedImages = computed(() => 
  imageLogs.value.filter(log => log.status === 'Aprovado').length
)

const rejectedImages = computed(() => 
  imageLogs.value.filter(log => log.status === 'Reprovado').length
)

const errorImages = computed(() => 
  imageLogs.value.filter(log => log.status === 'Erro').length
)
</script>
