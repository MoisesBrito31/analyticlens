<template>
  <div>
    <TopMenu />
    <BContainer fluid class="mt-4">
      <BRow>
        <BCol cols="12">
          <BCard class="shadow-sm border-0">
            <BCardHeader class="bg-success text-white">
              <div class="d-flex align-items-center">
                <Icon name="clipboard-check" size="1.5rem" class="me-3" />
                <div>
                  <h2 class="mb-0">Sistema de Inspeções</h2>
                  <p class="mb-0 opacity-75">Gerencie e monitore suas inspeções de visão computacional</p>
                </div>
              </div>
            </BCardHeader>
            <BCardBody class="p-4 p-md-5">
              <BRow>
                <BCol cols="12">
                  <InspectionsTable
                    :inspections="inspections"
                    :loading="loading"
                    @refresh="loadInspections"
                    @edit-offline="goEditOffline"
                  />
                </BCol>
              </BRow>
              
              <BRow class="mt-4">
                <BCol cols="12">
                  <hr class="my-4">
                  <div class="d-flex justify-content-between align-items-center">
                    <small class="text-muted">
                      <Icon name="clock" size="1rem" class="me-1" />
                      Última verificação: {{ new Date().toLocaleString('pt-BR') }}
                    </small>
                    <div></div>
                  </div>
                </BCol>
              </BRow>
            </BCardBody>
          </BCard>
        </BCol>
      </BRow>
    </BContainer>
  </div>
</template>

<script setup>
import TopMenu from '@/components/TopMenu.vue'
import Icon from '@/components/Icon.vue'
import InspectionsTable from '@/components/InspectionsTable.vue'
import { ref, computed, onMounted } from 'vue'
import { apiFetch } from '@/utils/http'
import {
  BContainer,
  BRow,
  BCol,
  BCard,
  BCardHeader,
  BCardBody,
  BAlert,
  BButton,
  BTable
} from 'bootstrap-vue-3'

// Estado da tabela de inspeções
const inspections = ref([])
const loading = ref(false)

const fields = [
  { key: 'name', label: 'Inspeção' },
  { key: 'vm_name', label: 'VM' },
  { key: 'tools', label: 'Ferramentas (nome e tipo)' }
]

const tableItems = computed(() =>
  inspections.value.map((insp) => ({
    name: insp.name || '-',
    vm_name: insp.vm?.name || insp.vm_name || '-',
    tools: Array.isArray(insp.tools)
      ? insp.tools.map(t => `${t.name} (${t.type})`).join(', ')
      : '-'
  }))
)

async function loadInspections() {
  loading.value = true
  try {
    const res = await apiFetch('/api/inspections')
    const data = await res.json()
    inspections.value = Array.isArray(data) ? data : (data?.inspections || [])
  } catch (e) {
    // Fallback em erro
    inspections.value = []
  } finally {
    loading.value = false
  }
}

onMounted(loadInspections)

function goEditOffline(row) {
  if (!row || !row.raw?.id) return
  window.location.href = `/inspections/${row.raw.id}/edit`
}
</script>

<style scoped>
.card-header {
  background: linear-gradient(135deg, #198754 0%, #20c997 100%) !important;
}

.opacity-75 {
  opacity: 0.75;
}

.fs-2 {
  font-size: 1.5rem !important;
}

/* Responsividade para telas menores */
@media (max-width: 768px) {
  .container-fluid {
    padding-left: 0.5rem !important;
    padding-right: 0.5rem !important;
  }
  
  .card-body {
    padding: 1rem !important;
  }
  
  .card-header {
    padding: 1rem !important;
  }
  
  .card-header h2 {
    font-size: 1.5rem !important;
  }
  
  .card-header p {
    font-size: 0.9rem !important;
  }
  
  .fs-2 {
    font-size: 1.25rem !important;
  }
  
  .py-4.py-md-5 {
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
  }
}

@media (max-width: 576px) {
  .container-fluid {
    padding-left: 0.25rem !important;
    padding-right: 0.25rem !important;
  }
  
  .mt-4 {
    margin-top: 0.5rem !important;
  }
  
  .card-body {
    padding: 0.75rem !important;
  }
  
  .card-header {
    padding: 0.75rem !important;
  }
  
  .card-header h2 {
    font-size: 1.25rem !important;
  }
  
  .card-header p {
    font-size: 0.8rem !important;
  }
  
  .fs-2 {
    font-size: 1.1rem !important;
  }
  
  .py-4.py-md-5 {
    padding-top: 1.5rem !important;
    padding-bottom: 1.5rem !important;
  }
  
  .d-flex.justify-content-between {
    flex-direction: column !important;
    gap: 0.5rem !important;
    align-items: stretch !important;
  }
  
  .d-flex.justify-content-between .btn {
    width: 100% !important;
  }
}
</style>
