<template>
  <div>
    <TopMenu />
    <BContainer fluid class="mt-4">
      <BRow>
        <BCol cols="12">
          <BCard class="shadow-sm border-0">
            <BCardHeader class="bg-info text-white">
              <div class="d-flex align-items-center">
                <Icon name="cpu" size="1.5rem" class="me-3" />
                <div>
                  <h2 class="mb-0">Lista de Máquinas de Visão (VM)</h2>
                  <p class="mb-0 opacity-75">Gerencie suas máquinas de visão conectadas</p>
                </div>
              </div>
            </BCardHeader>
            <BCardBody class="p-4 p-md-5">
              <!-- Modal: Criar VM -->
              <BModal v-model="showCreateModal" title="Criar Nova VM" hide-footer>
                <BForm @submit.prevent="submitCreateVM">
                  <BRow>
                    <BCol cols="12" md="6">
                      <BFormGroup label="ID da Máquina" label-for="machine_id" label-cols-sm="12">
                        <BFormInput id="machine_id" v-model="form.machine_id" required placeholder="Ex.: VM001" />
                      </BFormGroup>
                    </BCol>
                    <BCol cols="12" md="6">
                      <BFormGroup label="Nome" label-for="name" label-cols-sm="12">
                        <BFormInput id="name" v-model="form.name" required placeholder="Ex.: VM da Linha 1" />
                      </BFormGroup>
                    </BCol>
                    <BCol cols="12" md="6">
                      <BFormGroup label="Modo" label-for="mode" label-cols-sm="12">
                        <BFormSelect id="mode" v-model="form.mode" :options="modeOptions" required />
                      </BFormGroup>
                    </BCol>
                    <BCol cols="12" md="6">
                      <BFormGroup label="Fonte" label-for="source_type" label-cols-sm="12">
                        <BFormSelect id="source_type" v-model="form.source_type" :options="sourceOptions" />
                      </BFormGroup>
                    </BCol>
                    <BCol cols="12" md="6">
                      <BFormGroup label="IP (opcional)" label-for="ip" label-cols-sm="12">
                        <BFormInput id="ip" v-model="form.ip_address" placeholder="Ex.: 192.168.0.10" />
                      </BFormGroup>
                    </BCol>
                    <BCol cols="12" md="6">
                      <BFormGroup label="Porta (opcional)" label-for="port" label-cols-sm="12">
                        <BFormInput id="port" v-model.number="form.port" type="number" min="1" max="65535" placeholder="Ex.: 5000" />
                      </BFormGroup>
                    </BCol>
                  </BRow>

                  <div class="d-flex justify-content-end gap-2 mt-2">
                    <BButton variant="secondary" @click="closeCreateModal" :disabled="submitting">Cancelar</BButton>
                    <BButton variant="primary" type="submit" :disabled="submitting">
                      <Icon name="plus" size="1rem" class="me-1" />
                      {{ submitting ? 'Criando...' : 'Criar VM' }}
                    </BButton>
                  </div>
                  <div v-if="errorMessage" class="text-danger mt-2">{{ errorMessage }}</div>
                </BForm>
              </BModal>

              <!-- Componente da tabela de VMs -->
              <VMsTable
                ref="vmsTableRef"
                :refresh-interval="30000"
                @vm-action="handleVMAction"
                @refresh="handleRefresh"
                @error="handleError"
              />
              
              <!-- Informações adicionais -->
              <BRow class="mt-4">
                <BCol cols="12">
                  <hr class="my-4">
                  <div class="d-flex justify-content-between align-items-center">
                    <small class="text-muted">
                      <Icon name="clock" size="1rem" class="me-1" />
                      Última verificação: {{ lastCheckTime }}
                    </small>
                    <div class="d-flex gap-2">
                      <BButton
                        variant="outline-success"
                        size="sm"
                        @click="openCreateModal"
                      >
                        <Icon name="plus" size="1rem" class="me-1" />
                        Nova VM
                      </BButton>
                      <BButton
                        variant="outline-primary"
                        size="sm"
                        @click="refreshTable"
                      >
                        <Icon name="arrow-clockwise" size="1rem" class="me-1" />
                        Atualizar
                      </BButton>
                    </div>
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
import { ref, onMounted } from 'vue'
// import { useRouter } from 'vue-router'
import TopMenu from '@/components/TopMenu.vue'
import Icon from '@/components/Icon.vue'
import VMsTable from '@/components/VMsTable.vue'
import { apiFetch } from '@/utils/http'
import {
  BContainer,
  BRow,
  BCol,
  BCard,
  BCardHeader,
  BCardBody,
  BButton,
  BModal,
  BForm,
  BFormGroup,
  BFormInput,
  BFormSelect
} from 'bootstrap-vue-3'

// Router (não utilizado após uso do modal)
// const router = useRouter()

// Refs
const vmsTableRef = ref(null)
const lastCheckTime = ref('')
const showCreateModal = ref(false)
const submitting = ref(false)
const errorMessage = ref('')
const form = ref({
  machine_id: '',
  name: '',
  mode: 'TESTE',
  source_type: 'camera',
  ip_address: '',
  port: 5000
})

const modeOptions = [
  { value: 'TESTE', text: 'Teste' },
  { value: 'PRODUCAO', text: 'Produção' }
]

const sourceOptions = [
  { value: 'camera', text: 'Câmera' },
  { value: 'rtsp', text: 'RTSP' },
  { value: 'pasta', text: 'Pasta' }
]

// Métodos
const handleVMAction = (actionData) => {
  if (actionData.success) {
    console.log(`VM ${actionData.action} executada com sucesso para VM ${actionData.vmId}`)
    // Aqui você pode adicionar notificações de sucesso
  } else {
    console.error(`Erro ao executar ${actionData.action} na VM ${actionData.vmId}:`, actionData.error)
    // Aqui você pode adicionar notificações de erro
  }
}

const handleRefresh = () => {
  lastCheckTime.value = new Date().toLocaleString('pt-BR')
}

const handleError = (errorMessage) => {
  console.error('Erro na tabela de VMs:', errorMessage)
  // Aqui você pode adicionar notificações de erro
}

const refreshTable = () => {
  if (vmsTableRef.value) {
    vmsTableRef.value.refresh()
  }
}

const openCreateModal = () => {
  showCreateModal.value = true
}

const closeCreateModal = () => {
  showCreateModal.value = false
  errorMessage.value = ''
}

const submitCreateVM = async () => {
  try {
    submitting.value = true
    errorMessage.value = ''
    // Montar payload mínimo aceito pela API
    const payload = {
      machine_id: form.value.machine_id.trim(),
      name: form.value.name.trim(),
      mode: form.value.mode,
      source_type: form.value.source_type,
      ip_address: form.value.ip_address || '',
      port: form.value.port || 5000
    }
    if (!payload.machine_id || !payload.name) {
      errorMessage.value = 'Preencha os campos obrigatórios.'
      return
    }
    const res = await apiFetch('/api/vms', {
      method: 'POST',
      body: JSON.stringify(payload)
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err?.erro || `Falha ao criar VM (HTTP ${res.status})`)
    }
    // Sucesso: fechar modal e atualizar tabela
    closeCreateModal()
    // Reset form
    form.value = {
      machine_id: '',
      name: '',
      mode: 'TESTE',
      source_type: 'camera',
      ip_address: '',
      port: 5000
    }
    refreshTable()
  } catch (e) {
    errorMessage.value = e.message
  } finally {
    submitting.value = false
  }
}

// Lifecycle
onMounted(() => {
  lastCheckTime.value = new Date().toLocaleString('pt-BR')
})
</script>

<style scoped>
/* Estilos específicos da view */
.bg-info {
  background: linear-gradient(135deg, #17a2b8 0%, #138496 100%) !important;
}

.opacity-75 {
  opacity: 0.75;
}

.gap-2 {
  gap: 0.5rem;
}

/* Responsividade */
@media (max-width: 768px) {
  .p-md-5 {
    padding: 1rem !important;
  }
  
  .d-flex.justify-content-between {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .d-flex.gap-2 {
    justify-content: center;
  }
}
</style>
