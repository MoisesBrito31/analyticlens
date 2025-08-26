<template>
  <div>
    <TopMenu />
    <BContainer fluid class="mt-4">
      <BRow>
        <BCol cols="12">
          <BCard class="shadow-sm border-0">
            <BCardHeader class="bg-secondary text-white">
              <div class="d-flex align-items-center justify-content-between">
                <div class="d-flex align-items-center">
                  <Icon name="clipboard-check" size="1.2rem" class="me-2" />
                  <h2 class="mb-0">Editar Inspeção (Offline)</h2>
                </div>
                <div class="d-flex gap-2">
                  <BButton variant="secondary" @click="goBack">Voltar</BButton>
                  <BButton :disabled="saving" variant="primary" @click="save">{{ saving ? 'Salvando...' : 'Salvar' }}</BButton>
                  <BButton :disabled="saving" variant="success" @click="updateVM">Atualizar VM</BButton>
                </div>
              </div>
            </BCardHeader>
            <BCardBody class="p-4">
              <div v-if="loading">Carregando...</div>
              <div v-else-if="error" class="text-danger">{{ error }}</div>
              <div v-else>
                <!-- Nome e descrição no topo -->
                <BRow class="mb-3 g-3">
                  <BCol cols="12" md="6">
                    <label class="form-label">Nome</label>
                    <BFormInput v-model="form.name" />
                  </BCol>
                  <BCol cols="12" md="6">
                    <label class="form-label">Descrição</label>
                    <BFormInput v-model="form.description" />
                  </BCol>
                </BRow>

                <!-- Linha com referência e parâmetros da tool selecionada -->
                <BRow class="g-3 mb-3 align-items-stretch">
                  <BCol cols="12" md="6">
                    <div class="ref-image-panel">
                      <div class="panel-title">Imagem de referência</div>
                      <div class="ref-image-wrapper">
                        <img v-if="refPreviewUrl" :src="refPreviewUrl" alt="referência" />
                        <div v-else class="text-muted small">Sem imagem de referência</div>
                      </div>
                    </div>
                  </BCol>
                  <BCol cols="12" md="6">
                    <div class="tool-params-panel">
                      <div class="panel-title">Parâmetros da ferramenta selecionada</div>
                      <div v-if="selectedTool">
                        <BRow class="g-2 mb-2">
                          <BCol cols="12" md="6">
                            <label class="form-label">Nome</label>
                            <BFormInput v-model="selectedTool.name" />
                          </BCol>
                          <BCol cols="12" md="6">
                            <label class="form-label">Tipo</label>
                            <BFormInput v-model="selectedTool.type" disabled />
                          </BCol>
                        </BRow>
                        <BRow class="g-2 mb-2">
                          <BCol cols="12">
                            <label class="form-label">Pass/Fail</label>
                            <div>
                              <input type="checkbox" v-model="selectedTool.inspec_pass_fail" />
                              <span class="ms-2">Considerar no resultado</span>
                            </div>
                          </BCol>
                        </BRow>
                        <div class="mb-1 fw-semibold small text-muted">ROI</div>
                        <BRow class="g-2 mb-2">
                          <BCol cols="6" md="3"><BFormInput v-model.number="selectedTool.ROI.x" type="number" placeholder="x" /></BCol>
                          <BCol cols="6" md="3"><BFormInput v-model.number="selectedTool.ROI.y" type="number" placeholder="y" /></BCol>
                          <BCol cols="6" md="3"><BFormInput v-model.number="selectedTool.ROI.w" type="number" placeholder="w" /></BCol>
                          <BCol cols="6" md="3"><BFormInput v-model.number="selectedTool.ROI.h" type="number" placeholder="h" /></BCol>
                        </BRow>

                        <!-- Específicos por tipo -->
                        <div v-if="selectedTool.type === 'grayscale'" class="mb-2">
                          <div class="mb-1 fw-semibold small text-muted">Grayscale</div>
                          <BRow class="g-2">
                            <BCol cols="12" md="6">
                              <label class="form-label">Método</label>
                              <BFormSelect v-model="selectedTool.method" :options="grayscaleMethods" />
                            </BCol>
                            <BCol cols="12" md="6" class="d-flex align-items-end">
                              <div>
                                <input type="checkbox" v-model="selectedTool.normalize" />
                                <span class="ms-2">Normalizar</span>
                              </div>
                            </BCol>
                          </BRow>
                        </div>

                        <div v-else-if="selectedTool.type === 'blur'" class="mb-2">
                          <div class="mb-1 fw-semibold small text-muted">Blur</div>
                          <BRow class="g-2">
                            <BCol cols="12" md="4">
                              <label class="form-label">Método</label>
                              <BFormSelect v-model="selectedTool.method" :options="blurMethods" />
                            </BCol>
                            <BCol cols="12" md="4">
                              <label class="form-label">Kernel</label>
                              <BFormInput v-model.number="selectedTool.ksize" type="number" />
                            </BCol>
                            <BCol cols="12" md="4">
                              <label class="form-label">Sigma</label>
                              <BFormInput v-model.number="selectedTool.sigma" type="number" step="0.01" />
                            </BCol>
                          </BRow>
                        </div>

                        <div v-else-if="selectedTool.type === 'threshold'" class="mb-2">
                          <div class="mb-1 fw-semibold small text-muted">Threshold</div>
                          <BRow class="g-2">
                            <BCol cols="12" md="4">
                              <label class="form-label">Modo</label>
                              <BFormSelect v-model="selectedTool.mode" :options="thresholdModes" />
                            </BCol>
                            <BCol cols="12" md="4">
                              <label class="form-label">Min</label>
                              <BFormInput v-model.number="selectedTool.th_min" type="number" />
                            </BCol>
                            <BCol cols="12" md="4">
                              <label class="form-label">Max</label>
                              <BFormInput v-model.number="selectedTool.th_max" type="number" />
                            </BCol>
                          </BRow>
                        </div>

                        <div v-else-if="selectedTool.type === 'morphology'" class="mb-2">
                          <div class="mb-1 fw-semibold small text-muted">Morphology</div>
                          <BRow class="g-2">
                            <BCol cols="12" md="3">
                              <label class="form-label">Kernel</label>
                              <BFormInput v-model.number="selectedTool.kernel" type="number" />
                            </BCol>
                            <BCol cols="12" md="3">
                              <label class="form-label">Open</label>
                              <BFormInput v-model.number="selectedTool.open" type="number" />
                            </BCol>
                            <BCol cols="12" md="3">
                              <label class="form-label">Close</label>
                              <BFormInput v-model.number="selectedTool.close" type="number" />
                            </BCol>
                            <BCol cols="12" md="3">
                              <label class="form-label">Shape</label>
                              <BFormSelect v-model="selectedTool.shape" :options="morphShapes" />
                            </BCol>
                          </BRow>
                        </div>

                        <div v-else-if="selectedTool.type === 'blob'" class="mb-2">
                          <div class="mb-1 fw-semibold small text-muted">Blob</div>
                          <BRow class="g-2">
                            <BCol cols="6" md="3"><label class="form-label small">th_min</label><BFormInput v-model.number="selectedTool.th_min" type="number" /></BCol>
                            <BCol cols="6" md="3"><label class="form-label small">th_max</label><BFormInput v-model.number="selectedTool.th_max" type="number" /></BCol>
                            <BCol cols="6" md="3"><label class="form-label small">area_min</label><BFormInput v-model.number="selectedTool.area_min" type="number" step="0.01" /></BCol>
                            <BCol cols="6" md="3"><label class="form-label small">area_max</label><BFormInput v-model.number="selectedTool.area_max" type="number" step="0.01" /></BCol>
                            <BCol cols="12" class="mt-1">
                              <input type="checkbox" v-model="selectedTool.total_area_test" /> <span class="me-3">Testar área total</span>
                              <input type="checkbox" v-model="selectedTool.blob_count_test" /> <span>Testar contagem</span>
                            </BCol>
                            <BCol cols="6" md="3"><label class="form-label small">total_area_min</label><BFormInput v-model.number="selectedTool.test_total_area_min" type="number" step="0.01" /></BCol>
                            <BCol cols="6" md="3"><label class="form-label small">total_area_max</label><BFormInput v-model.number="selectedTool.test_total_area_max" type="number" step="0.01" /></BCol>
                            <BCol cols="6" md="3"><label class="form-label small">blob_count_min</label><BFormInput v-model.number="selectedTool.test_blob_count_min" type="number" /></BCol>
                            <BCol cols="6" md="3"><label class="form-label small">blob_count_max</label><BFormInput v-model.number="selectedTool.test_blob_count_max" type="number" /></BCol>
                            <BCol cols="6" md="6"><label class="form-label small">contour_chain</label><BFormSelect v-model="selectedTool.contour_chain" :options="contourChains" /></BCol>
                            <BCol cols="6" md="3"><label class="form-label small">approx_epsilon_ratio</label><BFormInput v-model.number="selectedTool.approx_epsilon_ratio" type="number" step="0.001" /></BCol>
                            <BCol cols="6" md="3"><label class="form-label small">polygon_max_points</label><BFormInput v-model.number="selectedTool.polygon_max_points" type="number" /></BCol>
                          </BRow>
                        </div>

                        <div v-else-if="selectedTool.type === 'math'" class="mb-2">
                          <div class="mb-1 fw-semibold small text-muted">Math</div>
                          <BRow class="g-2">
                            <BCol cols="12" md="4"><label class="form-label">Operação</label><BFormSelect v-model="selectedTool.operation" :options="mathOps" /></BCol>
                            <BCol cols="12" md="4"><label class="form-label">Ref Tool ID</label><BFormInput v-model.number="selectedTool.reference_tool_id" type="number" /></BCol>
                            <BCol cols="12" md="4"><label class="form-label">Fórmula</label><BFormInput v-model="selectedTool.custom_formula" /></BCol>
                          </BRow>
                        </div>

                        <div class="small text-muted">Clique em uma linha abaixo para selecionar.</div>
                      </div>
                      <div v-else class="text-muted small">Selecione uma ferramenta na tabela para editar seus parâmetros.</div>
                    </div>
                  </BCol>
                </BRow>

                <div class="mb-2 fw-semibold">Ferramentas</div>
                <BTable :items="toolsItems" :fields="toolsFields" small responsive hover class="mb-3" @row-clicked="onRowClicked">
                  <template #cell(ROI)="{ item }">
                    <div class="d-flex gap-1 flex-wrap">
                      <BFormInput v-model.number="item.ROI.x" type="number" size="sm" placeholder="x" style="width: 80px" />
                      <BFormInput v-model.number="item.ROI.y" type="number" size="sm" placeholder="y" style="width: 80px" />
                      <BFormInput v-model.number="item.ROI.w" type="number" size="sm" placeholder="w" style="width: 80px" />
                      <BFormInput v-model.number="item.ROI.h" type="number" size="sm" placeholder="h" style="width: 80px" />
                    </div>
                  </template>
                  <template #cell(actions)="{ index }">
                    <div class="d-flex justify-content-end gap-1">
                      <BButton size="sm" variant="outline-secondary" @click="moveUp(index)" :disabled="index === 0" title="Subir">
                        <Icon name="arrow-up" size="0.8rem" />
                      </BButton>
                      <BButton size="sm" variant="outline-secondary" @click="moveDown(index)" :disabled="index === toolsItems.length - 1" title="Descer">
                        <Icon name="arrow-down" size="0.8rem" />
                      </BButton>
                      <BButton size="sm" variant="danger" @click="removeTool(index)">Remover</BButton>
                    </div>
                  </template>
                </BTable>

                <div class="d-flex gap-2 align-items-center">
                  <div class="text-muted small me-2">Adicionar ferramenta:</div>
                  <BButton size="sm" variant="outline-secondary" @click="addTool('grayscale')">Grayscale</BButton>
                  <BButton size="sm" variant="outline-secondary" @click="addTool('blur')">Blur</BButton>
                  <BButton size="sm" variant="outline-secondary" @click="addTool('threshold')">Threshold</BButton>
                  <BButton size="sm" variant="outline-secondary" @click="addTool('morphology')">Morphology</BButton>
                  <BButton size="sm" variant="outline-secondary" @click="addTool('blob')">Blob</BButton>
                  <BButton size="sm" variant="outline-secondary" @click="addTool('math')">Math</BButton>
                </div>

                <div class="mt-4 d-flex justify-content-end gap-2">
                  <BButton variant="outline-primary" @click="showJson">Visualizar JSON</BButton>
                </div>
              </div>
            </BCardBody>
          </BCard>
        </BCol>
      </BRow>
    </BContainer>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import TopMenu from '@/components/TopMenu.vue'
import Icon from '@/components/Icon.vue'
import { apiFetch } from '@/utils/http'
import getMediaUrl from '@/utils/mediaRouter'
import { BContainer, BRow, BCol, BCard, BCardHeader, BCardBody, BButton, BTable, BFormInput, BFormSelect } from 'bootstrap-vue-3'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const saving = ref(false)
const error = ref('')
const inspId = ref(null)

const form = ref({ name: '', description: '' })
const toolsItems = ref([])
const selectedIdx = ref(-1)
const refImagePath = ref('')
const refPreviewUrl = ref('')
const toolsFields = [
  { key: 'order_index', label: '#', class: 'text-center' },
  { key: 'name', label: 'Nome' },
  { key: 'type', label: 'Tipo' },
  { key: 'ROI', label: 'ROI' },
  { key: 'inspec_pass_fail', label: 'Pass/Fail', class: 'text-center' },
  { key: 'actions', label: 'Ações', class: 'text-end' }
]

const grayscaleMethods = [
  { value: 'luminance', text: 'Luminance' },
  { value: 'average', text: 'Average' },
  { value: 'weighted', text: 'Weighted' }
]
const blurMethods = [
  { value: 'gaussian', text: 'Gaussian' },
  { value: 'median', text: 'Median' }
]
const thresholdModes = [
  { value: 'binary', text: 'Binary' },
  { value: 'range', text: 'Range' },
  { value: 'otsu', text: 'Otsu' }
]
const morphShapes = [
  { value: 'ellipse', text: 'Ellipse' },
  { value: 'rect', text: 'Rect' },
  { value: 'cross', text: 'Cross' }
]
const contourChains = [
  { value: 'SIMPLE', text: 'SIMPLE' },
  { value: 'NONE', text: 'NONE' },
  { value: 'TC89_L1', text: 'TC89_L1' },
  { value: 'TC89_KCOS', text: 'TC89_KCOS' }
]
const mathOps = [
  { value: 'area_ratio', text: 'Area Ratio' },
  { value: 'blob_density', text: 'Blob Density' },
  { value: 'custom_formula', text: 'Custom Formula' }
]

function goBack() {
  router.push('/inspections')
}

function addTool(type) {
  const idx = toolsItems.value.length
  const base = { order_index: idx, name: `${type}_${idx + 1}`, type, inspec_pass_fail: false }
  const roiFull = { x: 0, y: 0, w: 752, h: 480 }
  let tool = {}
  if (type === 'grayscale') {
    tool = { ...base, ROI: roiFull, method: 'luminance', normalize: false }
  } else if (type === 'blur') {
    tool = { ...base, ROI: roiFull, method: 'gaussian', ksize: 5, sigma: 0.8 }
  } else if (type === 'threshold') {
    tool = { ...base, ROI: roiFull, mode: 'range', th_min: 130, th_max: 255 }
  } else if (type === 'morphology') {
    tool = { ...base, ROI: roiFull, kernel: 3, open: 1, close: 1, shape: 'ellipse' }
  } else if (type === 'blob') {
    tool = {
      ...base,
      ROI: roiFull,
      th_min: 130,
      th_max: 255,
      area_min: 100,
      area_max: 10000000,
      total_area_test: true,
      blob_count_test: true,
      test_total_area_min: 50,
      test_total_area_max: 10000,
      test_blob_count_min: 1,
      test_blob_count_max: 10000,
      contour_chain: 'TC89_KCOS',
      approx_epsilon_ratio: 0.003,
      polygon_max_points: 1000,
      inspec_pass_fail: true
    }
  } else {
    tool = { ...base, ROI: roiFull }
  }
  toolsItems.value.push(tool)
}

function removeTool(index) {
  toolsItems.value.splice(index, 1)
  toolsItems.value.forEach((t, i) => (t.order_index = i))
}

function moveUp(index) {
  if (index <= 0) return
  const arr = toolsItems.value
  ;[arr[index - 1], arr[index]] = [arr[index], arr[index - 1]]
  arr.forEach((t, i) => (t.order_index = i))
}

function moveDown(index) {
  const arr = toolsItems.value
  if (index >= arr.length - 1) return
  ;[arr[index + 1], arr[index]] = [arr[index], arr[index + 1]]
  arr.forEach((t, i) => (t.order_index = i))
}

async function load() {
  try {
    loading.value = true
    error.value = ''
    const id = route.params.id
    inspId.value = id
    const res = await apiFetch(`/api/inspections/${id}`)
    const data = await res.json()
    form.value.name = data.name
    form.value.description = data.description || ''
    toolsItems.value = Array.isArray(data.tools) ? data.tools.map(t => ({ ...t })) : []
    // Guardar vmId para redirecionamento após updateVM
    if (data.vm && typeof data.vm.id !== 'undefined')
      sessionStorage.setItem(`insp_vm_${id}`, String(data.vm.id))
    if (data.reference_image_url) {
      // Deriva path relativo e monta URL correta conforme ambiente
      refImagePath.value = String(data.reference_image_url).replace(/^.*\/media\//, '')
      refPreviewUrl.value = getMediaUrl(refImagePath.value)
    } else {
      refImagePath.value = ''
      refPreviewUrl.value = ''
    }
  } catch (e) {
    error.value = e.message || 'Erro ao carregar inspeção'
  } finally {
    loading.value = false
  }
}

async function save() {
  try {
    saving.value = true
    const payload = {
      name: form.value.name,
      description: form.value.description,
      tools: toolsItems.value.map(t => ({
        order_index: t.order_index,
        name: t.name,
        type: t.type,
        ROI: t.ROI,
        inspec_pass_fail: !!t.inspec_pass_fail,
        method: t.method,
        normalize: t.normalize,
        ksize: t.ksize,
        sigma: t.sigma,
        mode: t.mode,
        th_min: t.th_min,
        th_max: t.th_max,
        kernel: t.kernel,
        open: t.open,
        close: t.close,
        shape: t.shape,
        area_min: t.area_min,
        area_max: t.area_max,
        total_area_test: t.total_area_test,
        blob_count_test: t.blob_count_test,
        test_total_area_min: t.test_total_area_min,
        test_total_area_max: t.test_total_area_max,
        test_blob_count_min: t.test_blob_count_min,
        test_blob_count_max: t.test_blob_count_max,
        contour_chain: t.contour_chain,
        approx_epsilon_ratio: t.approx_epsilon_ratio,
        polygon_max_points: t.polygon_max_points,
        operation: t.operation,
        reference_tool_id: t.reference_tool_id,
        custom_formula: t.custom_formula
      }))
    }
    const res = await apiFetch(`/api/inspections/${inspId.value}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    if (!res.ok) throw new Error('Falha ao salvar')
    goBack()
  } catch (e) {
    error.value = e.message || 'Erro ao salvar'
  } finally {
    saving.value = false
  }
}

function showJson() {
  const preview = { tools: toolsItems.value }
  alert(JSON.stringify(preview, null, 2))
}

async function updateVM() {
  try {
    saving.value = true
    const payload = { tools: toolsItems.value.map(t => ({
      order_index: t.order_index,
      name: t.name,
      type: t.type,
      ROI: t.ROI,
      inspec_pass_fail: !!t.inspec_pass_fail,
      method: t.method,
      normalize: t.normalize,
      ksize: t.ksize,
      sigma: t.sigma,
      mode: t.mode,
      th_min: t.th_min,
      th_max: t.th_max,
      kernel: t.kernel,
      open: t.open,
      close: t.close,
      shape: t.shape,
      area_min: t.area_min,
      area_max: t.area_max,
      total_area_test: t.total_area_test,
      blob_count_test: t.blob_count_test,
      test_total_area_min: t.test_total_area_min,
      test_total_area_max: t.test_total_area_max,
      test_blob_count_min: t.test_blob_count_min,
      test_blob_count_max: t.test_blob_count_max,
      contour_chain: t.contour_chain,
      approx_epsilon_ratio: t.approx_epsilon_ratio,
      polygon_max_points: t.polygon_max_points,
      operation: t.operation,
      reference_tool_id: t.reference_tool_id,
      custom_formula: t.custom_formula
    })) }
    const res = await apiFetch(`/api/inspections/${inspId.value}/update_vm`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    if (!res.ok) throw new Error('Falha ao atualizar VM')
    // Atualiza a inspeção offline (PUT) para refletir na lista
    await save()
    // Redireciona para o AoVivo da VM correspondente
    router.push(`/machines/${vmIdFromQuery()}`)
  } catch (e) {
    alert(e.message || 'Erro ao atualizar VM')
  } finally {
    saving.value = false
  }
}

function vmIdFromQuery() {
  // Tenta extrair vmId se vier na rota (?vm=ID); se não, tenta usar a inspeção carregada (não retornamos vmId no GET atual)
  const q = new URLSearchParams(window.location.search)
  const v = q.get('vm')
  if (v) return v
  // fallback: tenta obter via API de inspeção atual
  // como não temos vmId no estado, retornamos vazio para não quebrar
  const id = route.params.id
  return sessionStorage.getItem(`insp_vm_${id}`) || ''
}

onMounted(load)

function onRowClicked(item, index) {
  selectedIdx.value = index
}

const selectedTool = computed(() => {
  if (selectedIdx.value < 0 || selectedIdx.value >= toolsItems.value.length) return null
  return toolsItems.value[selectedIdx.value]
})
</script>

<style scoped>
.bg-secondary {
  background: linear-gradient(135deg, #6c757d 0%, #5c636a 100%) !important;
}
</style>


