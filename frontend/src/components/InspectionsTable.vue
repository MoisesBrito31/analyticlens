<template>
  <div>
    <div class="d-flex align-items-center mb-3">
      <BAlert variant="success" show class="mb-0 flex-grow-1">
        <Icon name="info-circle" size="1.2rem" class="me-2" />
        <strong>Inspeções:</strong> visão geral das receitas salvas no orquestrador
      </BAlert>
    </div>

    <div class="table-container">
      <BTable
        :items="tableItems"
        :fields="fields"
        :busy="loading"
        striped
        hover
        responsive
        class="shadow-sm"
        empty-text="Nenhuma inspeção encontrada"
      >
        <!-- Miniatura -->
        <template #cell(preview)="{ item }">
          <div class="thumb" v-if="item.preview">
            <img :src="item.preview" alt="preview" />
          </div>
          <div v-else class="text-muted small">—</div>
        </template>
        <!-- Ações -->
        <template #cell(actions)="{ item }">
          <div class="d-flex gap-1 justify-content-end">
            
            <BButton size="sm" variant="secondary" :to="`/inspections/${item.raw.id}/edit`" title="Editar Offline">
              <Icon name="pencil-square" size="0.8rem" />
            </BButton>
            <BButton size="sm" variant="info" @click="$emit('edit-online', item.raw)" title="Editar Online">
              <Icon name="cloud-arrow-up" size="0.8rem" />
            </BButton>
            <BButton size="sm" variant="success" @click="$emit('update-vm', item.raw)" title="Atualizar VM">
              <Icon name="arrow-clockwise" size="0.8rem" />
            </BButton>
            <BButton size="sm" variant="outline-primary" @click="$emit('duplicate', item.raw)" title="Duplicar">
              <Icon name="files" size="0.8rem" />
            </BButton>
            <BButton size="sm" variant="danger" @click="$emit('delete', item.raw)" title="Apagar">
              <Icon name="trash3-fill" size="0.8rem" />
            </BButton>
          </div>
        </template>

        <!-- Loading -->
        <template #table-busy>
          <div class="text-center my-4">
            <div class="spinner-border text-success" role="status">
              <span class="visually-hidden">Carregando...</span>
            </div>
            <div class="mt-2">Carregando inspeções...</div>
          </div>
        </template>
      </BTable>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import Icon from '@/components/Icon.vue'
import { BAlert, BButton, BTable } from 'bootstrap-vue-3'
import getMediaUrl from '@/utils/mediaRouter'

const props = defineProps({
  inspections: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false }
})

defineEmits(['edit-offline', 'edit-online', 'update-vm', 'duplicate', 'delete'])

const fields = [
  { key: 'preview', label: '', class: 'text-center', thStyle: { width: '64px' } },
  { key: 'name', label: 'Inspeção', sortable: true },
  { key: 'vm_name', label: 'VM', sortable: true },
  { key: 'tools', label: 'Ferramentas (nome e tipo)' },
  { key: 'actions', label: 'Ações', class: 'text-end' }
]

const tableItems = computed(() =>
  (props.inspections || []).map((insp) => ({
    raw: insp,
    name: insp.name || '-',
    vm_name: (insp.vm && insp.vm.name) || insp.vm_name || '-',
    tools: Array.isArray(insp.tools)
      ? insp.tools.map(t => `${t.name} (${t.type})`).join(', ')
      : '-',
    preview: insp.reference_image_url ? getMediaUrl(insp.reference_image_path || insp.reference_image_url.replace(/^.*\/media\//, '')) : null
  }))
)
</script>

<style scoped>
.table-container {
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.thumb {
  width: 56px;
  height: 42px;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  overflow: hidden;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: #f8f9fa;
}

.thumb img {
  max-width: 100%;
  max-height: 100%;
  object-fit: cover;
}
</style>


