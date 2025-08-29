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
                  <!-- Filtros -->
                  <div class="d-flex align-items-center gap-2 mb-2">
                    <label class="form-label mb-0">Filtrar por VM:</label>
                    <BFormSelect v-model="vmFilter" :options="vmFilterOptions" style="max-width: 280px" />
                  </div>

                  <InspectionsTable
                    :inspections="inspections"
                    :loading="loading"
                    @edit-offline="goEditOffline"
                    @update-vm="updateVMFromRow"
                    @duplicate="duplicateInspection"
                    @delete="confirmDelete"
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

    <!-- Modal de confirmação de exclusão -->
    <BModal v-model="showDeleteModal" title="Remover inspeção" hide-footer>
      <p>
        Tem certeza que deseja remover a inspeção
        <strong v-if="toDelete">{{ toDelete.name || ('ID ' + toDelete.id) }}</strong>?
      </p>
      <div v-if="deleteError" class="text-danger mb-2">{{ deleteError }}</div>
      <div class="d-flex justify-content-end gap-2">
        <BButton variant="secondary" @click="showDeleteModal = false" :disabled="deleting">Cancelar</BButton>
        <BButton variant="danger" @click="doDelete" :disabled="deleting">
          {{ deleting ? 'Removendo...' : 'Remover' }}
        </BButton>
      </div>
    </BModal>
  </div>
</template>

<script setup>
import TopMenu from '@/components/TopMenu.vue'
import Icon from '@/components/Icon.vue'
import InspectionsTable from '@/components/InspectionsTable.vue'
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { apiFetch } from '@/utils/http'
import { BFormSelect } from 'bootstrap-vue-3'
import {
  BContainer,
  BRow,
  BCol,
  BCard,
  BCardHeader,
  BCardBody,
  BAlert,
  BButton,
  BTable,
  BModal
} from 'bootstrap-vue-3'

// Estado da tabela de inspeções
const inspections = ref([])
const loading = ref(false)
const deleting = ref(false)
const deleteError = ref('')
const showDeleteModal = ref(false)
const toDelete = ref(null)
const router = useRouter()
const vmFilter = ref('')
const vmFilterOptions = ref([{ value: '', text: 'Todas as VMs' }])

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
    const query = vmFilter.value ? `?vm_id=${encodeURIComponent(vmFilter.value)}` : ''
    const res = await apiFetch(`/api/inspections${query}`)
    const data = await res.json()
    inspections.value = Array.isArray(data) ? data : (data?.inspections || [])
    // Popular opções de filtro de VM uma vez
    const vms = new Map()
    for (const it of inspections.value) {
      if (it.vm && it.vm.id) vms.set(String(it.vm.id), it.vm.name || `VM ${it.vm.id}`)
    }
    vmFilterOptions.value = [{ value: '', text: 'Todas as VMs' }, ...Array.from(vms.entries()).map(([id, name]) => ({ value: id, text: name }))]
  } catch (e) {
    // Fallback em erro
    inspections.value = []
  } finally {
    loading.value = false
  }
}

onMounted(loadInspections)

// Atualiza automaticamente quando o filtro muda
watch(vmFilter, () => {
  loadInspections()
})

function goEditOffline(row) {
  if (!row || !row.raw?.id) return
  window.location.href = `/inspections/${row.raw.id}/edit`
}

function confirmDelete(insp) {
  if (!insp || !insp.id) return
  toDelete.value = { id: insp.id, name: insp.name }
  deleteError.value = ''
  showDeleteModal.value = true
}

async function doDelete() {
  if (!toDelete.value) return
  try {
    deleting.value = true
    deleteError.value = ''
    const res = await apiFetch(`/api/inspections/${toDelete.value.id}`, { method: 'DELETE' })
    if (!res.ok) throw new Error('Falha ao remover')
    showDeleteModal.value = false
    toDelete.value = null
    await loadInspections()
  } catch (e) {
    deleteError.value = e.message || 'Erro ao remover'
  } finally {
    deleting.value = false
  }
}

// Atualizar VM a partir da inspeção selecionada (republicar configuração atual da inspeção na VM relacionada)
async function updateVMFromRow(insp) {
  try {
    if (!insp || !insp.id) return
    // Buscar detalhes completos da inspeção para enviar todos os parâmetros das tools
    const detRes = await apiFetch(`/api/inspections/${insp.id}`)
    const det = await detRes.json()
    const toolsPayload = Array.isArray(det.tools) ? det.tools : []

    const res = await apiFetch(`/api/inspections/${insp.id}/update_vm`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tools: toolsPayload })
    })
    if (!res.ok) throw new Error('Falha ao atualizar VM')
    // Redireciona para visão Ao Vivo da VM associada
    const vmId = (det && det.vm && det.vm.id) ? det.vm.id : (insp.vm && insp.vm.id ? insp.vm.id : null)
    if (vmId) {
      router.push(`/machines/${vmId}`)
    } else {
      await loadInspections()
    }
  } catch (e) {
    alert(e.message || 'Erro ao atualizar VM a partir da inspeção')
  }
}

// Duplicar inspeção: cria uma nova com sufixo "_copy" e mantém mesma VM e tools
async function duplicateInspection(insp) {
  try {
    if (!insp || !insp.id) return
    // Buscar detalhes
    const detRes = await apiFetch(`/api/inspections/${insp.id}`)
    const det = await detRes.json()
    const vmId = det?.vm?.id || null
    const name = `${det.name || 'inspec'}_copy`
    // Enviar via endpoint de salvar inspeção da VM (reuso):
    if (!vmId) {
      alert('Não foi possível duplicar: inspeção sem VM associada.')
      return
    }
    const payload = {
      name,
      overwrite: false,
      payload: { tools: det.tools, reference_image_url: det.reference_image_url }
    }
    const saveRes = await apiFetch(`/api/vms/${vmId}/inspections/save`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    if (!saveRes.ok) throw new Error('Falha ao duplicar inspeção')
    await loadInspections()
  } catch (e) {
    alert(e.message || 'Erro ao duplicar inspeção')
  }
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
