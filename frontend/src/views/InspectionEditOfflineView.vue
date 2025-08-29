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
                  <BCol cols="12" md="6">
                    <label class="form-label">Associar à VM</label>
                    <BFormSelect v-model="selectedVmId" :options="vmOptions" />
                  </BCol>
                </BRow>

                <!-- Linha com referência e parâmetros da tool selecionada -->
                <BRow class="g-3 mb-3 align-items-stretch">
                  <BCol cols="12" md="6">
                    <div class="ref-image-panel">
                      <div class="panel-title">Imagem de referência</div>
                      <div class="ref-image-wrapper">
                        <img
                          v-if="refPreviewUrl"
                          :src="refPreviewUrl"
                          alt="referência"
                          ref="refImgEl"
                          @load="onRefImageLoad"
                        />
                        <div v-else class="text-muted small">Sem imagem de referência</div>

                        <!-- Overlay de desenho/edição do ROI -->
                        <svg
                          v-if="refPreviewUrl && isOverlayActive"
                          class="roi-overlay"
                          :style="{ width: imgDisplayWidth + 'px', height: imgDisplayHeight + 'px' }"
                          :viewBox="`0 0 ${imgDisplayWidth} ${imgDisplayHeight}`"
                          @mousedown="onOverlayMouseDown"
                        >
                          <!-- Rect -->
                          <template v-if="currentShape === 'rect'">
                            <rect
                              v-if="displayRect.w > 0 && displayRect.h > 0"
                              :x="displayRect.x"
                              :y="displayRect.y"
                              :width="displayRect.w"
                              :height="displayRect.h"
                              class="roi-rect"
                              @mousedown.stop="startMove($event)"
                            />
                            <template v-if="displayRect.w > 0 && displayRect.h > 0">
                              <rect
                                v-for="h in handles"
                                :key="h.name"
                                class="roi-handle"
                                :x="h.x - handleSize/2"
                                :y="h.y - handleSize/2"
                                :width="handleSize"
                                :height="handleSize"
                                @mousedown.stop="startResize(h.name, $event)"
                              />
                            </template>
                          </template>

                          <!-- Circle -->
                          <template v-else-if="currentShape === 'circle'">
                            <circle
                              v-if="displayCircle.r > 0"
                              :cx="displayCircle.cx"
                              :cy="displayCircle.cy"
                              :r="displayCircle.r"
                              class="roi-rect"
                              @mousedown.stop="startMove($event)"
                            />
                            <template v-if="displayCircle.r > 0">
                              <rect v-for="h in circleHandles" :key="h.name" class="roi-handle" :x="h.x - handleSize/2" :y="h.y - handleSize/2" :width="handleSize" :height="handleSize" @mousedown.stop="startResize(h.name, $event)" />
                            </template>
                          </template>

                          <!-- Ellipse -->
                          <template v-else-if="currentShape === 'ellipse'">
                            <g :transform="`rotate(${displayEllipse.angle} ${displayEllipse.cx} ${displayEllipse.cy})`">
                              <ellipse
                                v-if="displayEllipse.rx > 0 && displayEllipse.ry > 0"
                                :cx="displayEllipse.cx"
                                :cy="displayEllipse.cy"
                                :rx="displayEllipse.rx"
                                :ry="displayEllipse.ry"
                                class="roi-rect"
                                @mousedown.stop="startMove($event)"
                              />
                            </g>
                          </template>
                        </svg>
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
                          <BCol cols="12" md="4">
                            <label class="form-label">Forma</label>
                            <BFormSelect v-model="selectedTool.ROI.shape" :options="shapeOptions" @change="onShapeChange" />
                          </BCol>
                        </BRow>
                        <BRow v-if="currentShape === 'rect'" class="g-2 mb-2">
                          <BCol cols="6" md="3"><BFormInput v-model.number="rectROI.x" type="number" placeholder="x" /></BCol>
                          <BCol cols="6" md="3"><BFormInput v-model.number="rectROI.y" type="number" placeholder="y" /></BCol>
                          <BCol cols="6" md="3"><BFormInput v-model.number="rectROI.w" type="number" placeholder="w" /></BCol>
                          <BCol cols="6" md="3" class="d-flex align-items-end justify-content-end">
                            <div class="w-100 d-flex gap-2">
                              <BFormInput v-model.number="rectROI.h" type="number" placeholder="h" />
                              <BButton size="sm" variant="success" @click="applyCurrentROI">Aplicar</BButton>
                            </div>
                          </BCol>
                        </BRow>
                        <BRow v-else-if="currentShape === 'circle'" class="g-2 mb-2">
                          <BCol cols="6" md="3"><BFormInput v-model.number="circleROI.cx" type="number" placeholder="cx" /></BCol>
                          <BCol cols="6" md="3"><BFormInput v-model.number="circleROI.cy" type="number" placeholder="cy" /></BCol>
                          <BCol cols="6" md="3" class="d-flex align-items-end justify-content-end">
                            <div class="w-100 d-flex gap-2">
                              <BFormInput v-model.number="circleROI.r" type="number" placeholder="r" />
                              <BButton size="sm" variant="success" @click="applyCurrentROI">Aplicar</BButton>
                            </div>
                          </BCol>
                        </BRow>
                        <BRow v-else-if="currentShape === 'ellipse'" class="g-2 mb-2">
                          <BCol cols="6" md="3"><BFormInput v-model.number="ellipseROI.cx" type="number" placeholder="cx" /></BCol>
                          <BCol cols="6" md="3"><BFormInput v-model.number="ellipseROI.cy" type="number" placeholder="cy" /></BCol>
                          <BCol cols="6" md="3"><BFormInput v-model.number="ellipseROI.rx" type="number" placeholder="rx" /></BCol>
                          <BCol cols="6" md="3"><BFormInput v-model.number="ellipseROI.ry" type="number" placeholder="ry" /></BCol>
                          <BCol cols="12" md="4" class="d-flex align-items-end justify-content-end">
                            <div class="w-100 d-flex gap-2">
                              <BFormInput v-model.number="ellipseROI.angle" type="number" placeholder="angle" />
                              <BButton size="sm" variant="success" @click="applyCurrentROI">Aplicar</BButton>
                            </div>
                          </BCol>
                        </BRow>
                        <div class="d-flex align-items-center gap-2 mb-2">
                          <BButton size="sm" variant="outline-primary" :disabled="!refPreviewUrl || !selectedTool" @click="toggleOverlay">
                            {{ isOverlayActive ? 'Concluir' : 'Desenhar' }}
                          </BButton>
                          <div v-if="isOverlayActive" class="small text-muted">Clique e arraste para desenhar; arraste o retângulo ou os pontos para ajustar.</div>
                        </div>

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
                    <div class="d-flex gap-1 flex-wrap align-items-center">
                      <template v-if="item.ROI && item.ROI.shape === 'rect' && item.ROI.rect">
                        <BFormInput v-model.number="item.ROI.rect.x" type="number" size="sm" placeholder="x" style="width: 80px" />
                        <BFormInput v-model.number="item.ROI.rect.y" type="number" size="sm" placeholder="y" style="width: 80px" />
                        <BFormInput v-model.number="item.ROI.rect.w" type="number" size="sm" placeholder="w" style="width: 80px" />
                        <BFormInput v-model.number="item.ROI.rect.h" type="number" size="sm" placeholder="h" style="width: 80px" />
                      </template>
                      <template v-else-if="item.ROI && (!item.ROI.shape || item.ROI.shape === 'rect')">
                        <BFormInput v-model.number="item.ROI.x" type="number" size="sm" placeholder="x" style="width: 80px" />
                        <BFormInput v-model.number="item.ROI.y" type="number" size="sm" placeholder="y" style="width: 80px" />
                        <BFormInput v-model.number="item.ROI.w" type="number" size="sm" placeholder="w" style="width: 80px" />
                        <BFormInput v-model.number="item.ROI.h" type="number" size="sm" placeholder="h" style="width: 80px" />
                      </template>
                      <template v-else-if="item.ROI && item.ROI.shape === 'circle'">
                        <span class="badge bg-primary">círculo</span>
                        <BFormInput v-model.number="item.ROI.circle.cx" type="number" size="sm" placeholder="cx" style="width: 80px" />
                        <BFormInput v-model.number="item.ROI.circle.cy" type="number" size="sm" placeholder="cy" style="width: 80px" />
                        <BFormInput v-model.number="item.ROI.circle.r" type="number" size="sm" placeholder="r" style="width: 80px" />
                      </template>
                      <template v-else-if="item.ROI && item.ROI.shape === 'ellipse'">
                        <span class="badge bg-primary">elipse</span>
                        <BFormInput v-model.number="item.ROI.ellipse.cx" type="number" size="sm" placeholder="cx" style="width: 80px" />
                        <BFormInput v-model.number="item.ROI.ellipse.cy" type="number" size="sm" placeholder="cy" style="width: 80px" />
                        <BFormInput v-model.number="item.ROI.ellipse.rx" type="number" size="sm" placeholder="rx" style="width: 80px" />
                        <BFormInput v-model.number="item.ROI.ellipse.ry" type="number" size="sm" placeholder="ry" style="width: 80px" />
                      </template>
                      <template v-else>
                        <span class="text-muted small">—</span>
                      </template>
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
                      <BButton size="sm" variant="outline-primary" @click="duplicateTool(index)" title="Duplicar">
                        <Icon name="files" size="0.8rem" />
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
                <div v-if="showJsonArea" class="mt-2">
                  <label class="form-label">Pré-visualização do JSON</label>
                  <BFormTextarea v-model="jsonPreview" rows="10" readonly class="font-monospace" />
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
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import TopMenu from '@/components/TopMenu.vue'
import Icon from '@/components/Icon.vue'
import { apiFetch } from '@/utils/http'
import getMediaUrl from '@/utils/mediaRouter'
import { BContainer, BRow, BCol, BCard, BCardHeader, BCardBody, BButton, BTable, BFormInput, BFormSelect, BFormTextarea } from 'bootstrap-vue-3'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const saving = ref(false)
const error = ref('')
const inspId = ref(null)

const form = ref({ name: '', description: '' })
const selectedVmId = ref('')
const vmOptions = ref([])
const toolsItems = ref([])
const selectedIdx = ref(-1)
const refImagePath = ref('')
const refPreviewUrl = ref('')
const refImgEl = ref(null)
const showJsonArea = ref(false)
const jsonPreview = ref('')

// Overlay de ROI
const isOverlayActive = ref(false)
const imgNaturalWidth = ref(0)
const imgNaturalHeight = ref(0)
const imgDisplayWidth = ref(0)
const imgDisplayHeight = ref(0)

const handleSize = 8
const interaction = ref({ mode: 'idle', startX: 0, startY: 0, baseRect: null, handle: '' })

const selectedTool = computed(() => {
  if (selectedIdx.value < 0 || selectedIdx.value >= toolsItems.value.length) return null
  return toolsItems.value[selectedIdx.value]
})

const currentShape = computed(() => {
  const t = selectedTool.value
  if (!t || !t.ROI) return 'rect'
  return t.ROI.shape || (('x' in t.ROI && 'y' in t.ROI && 'w' in t.ROI && 'h' in t.ROI) ? 'rect' : 'rect')
})

// Proxies por forma
const rectROI = computed({
  get() {
    const t = selectedTool.value; if (!t) return { x: 0, y: 0, w: 0, h: 0 }
    const r = t.ROI.rect || t.ROI
    return { x: r.x || 0, y: r.y || 0, w: r.w || 0, h: r.h || 0 }
  },
  set(v) {
    const t = selectedTool.value; if (!t) return
    if (!t.ROI) t.ROI = {}
    t.ROI.shape = 'rect'
    t.ROI.rect = { x: Number(v.x)||0, y: Number(v.y)||0, w: Number(v.w)||0, h: Number(v.h)||0 }
  }
})

const circleROI = computed({
  get() {
    const t = selectedTool.value; if (!t) return { cx: 0, cy: 0, r: 0 }
    const c = t.ROI.circle || { cx: 0, cy: 0, r: 0 }
    return { cx: c.cx || 0, cy: c.cy || 0, r: c.r || 0 }
  },
  set(v) {
    const t = selectedTool.value; if (!t) return
    if (!t.ROI) t.ROI = {}
    t.ROI.shape = 'circle'
    t.ROI.circle = { cx: Number(v.cx)||0, cy: Number(v.cy)||0, r: Number(v.r)||0 }
  }
})

const ellipseROI = computed({
  get() {
    const t = selectedTool.value; if (!t) return { cx: 0, cy: 0, rx: 0, ry: 0, angle: 0 }
    const e = t.ROI.ellipse || { cx: 0, cy: 0, rx: 0, ry: 0, angle: 0 }
    return { cx: e.cx || 0, cy: e.cy || 0, rx: e.rx || 0, ry: e.ry || 0, angle: e.angle || 0 }
  },
  set(v) {
    const t = selectedTool.value; if (!t) return
    if (!t.ROI) t.ROI = {}
    t.ROI.shape = 'ellipse'
    t.ROI.ellipse = { cx: Number(v.cx)||0, cy: Number(v.cy)||0, rx: Number(v.rx)||0, ry: Number(v.ry)||0, angle: Number(v.angle)||0 }
  }
})

function onShapeChange() {
  const t = selectedTool.value; if (!t) return
  if (!t.ROI) t.ROI = {}
  if (!t.ROI.shape) t.ROI.shape = 'rect'
  if (t.ROI.shape === 'rect' && !t.ROI.rect) t.ROI.rect = { x: 0, y: 0, w: imgNaturalWidth.value || 0, h: imgNaturalHeight.value || 0 }
  if (t.ROI.shape === 'circle' && !t.ROI.circle) t.ROI.circle = { cx: (imgNaturalWidth.value||0)/2, cy: (imgNaturalHeight.value||0)/2, r: Math.min((imgNaturalWidth.value||0),(imgNaturalHeight.value||0))/4 }
  if (t.ROI.shape === 'ellipse' && !t.ROI.ellipse) t.ROI.ellipse = { cx: (imgNaturalWidth.value||0)/2, cy: (imgNaturalHeight.value||0)/2, rx: (imgNaturalWidth.value||0)/4, ry: (imgNaturalHeight.value||0)/6, angle: 0 }
  // Remover chaves de outros shapes para evitar conflito
  if (t.ROI.shape === 'rect') {
    delete t.ROI.circle
    delete t.ROI.ellipse
    // remover legacy se usarmos rect aninhado
    if (t.ROI.rect) { delete t.ROI.x; delete t.ROI.y; delete t.ROI.w; delete t.ROI.h }
  } else if (t.ROI.shape === 'circle') {
    delete t.ROI.rect
    delete t.ROI.ellipse
    delete t.ROI.x; delete t.ROI.y; delete t.ROI.w; delete t.ROI.h
  } else if (t.ROI.shape === 'ellipse') {
    delete t.ROI.rect
    delete t.ROI.circle
    delete t.ROI.x; delete t.ROI.y; delete t.ROI.w; delete t.ROI.h
  }
}

function applyCurrentROI() {
  const t = selectedTool.value
  if (!t || !t.ROI) return
  if (t.ROI.shape === 'rect') {
    const r = rectROI.value
    t.ROI.rect = { x: Number(r.x)||0, y: Number(r.y)||0, w: Number(r.w)||0, h: Number(r.h)||0 }
    delete t.ROI.x; delete t.ROI.y; delete t.ROI.w; delete t.ROI.h
  } else if (t.ROI.shape === 'circle') {
    const c = circleROI.value
    t.ROI.circle = { cx: Number(c.cx)||0, cy: Number(c.cy)||0, r: Number(c.r)||0 }
  } else if (t.ROI.shape === 'ellipse') {
    const e = ellipseROI.value
    t.ROI.ellipse = { cx: Number(e.cx)||0, cy: Number(e.cy)||0, rx: Number(e.rx)||0, ry: Number(e.ry)||0, angle: Number(e.angle)||0 }
  }
  // noop
}

const displayRect = computed(() => {
  const t = selectedTool.value
  if (!t || !t.ROI) return { x: 0, y: 0, w: 0, h: 0 }
  const sx = imgDisplayWidth.value / (imgNaturalWidth.value || imgDisplayWidth.value || 1)
  const sy = imgDisplayHeight.value / (imgNaturalHeight.value || imgDisplayHeight.value || 1)
  const r = t.ROI.rect || t.ROI
  return {
    x: Math.max(0, Math.min(imgDisplayWidth.value, (r.x || 0) * sx)),
    y: Math.max(0, Math.min(imgDisplayHeight.value, (r.y || 0) * sy)),
    w: Math.max(0, Math.min(imgDisplayWidth.value - ((r.x || 0) * sx), (r.w || 0) * sx)),
    h: Math.max(0, Math.min(imgDisplayHeight.value - ((r.y || 0) * sy), (r.h || 0) * sy))
  }
})

const handles = computed(() => {
  const r = displayRect.value
  const cx = r.x + r.w / 2
  const cy = r.y + r.h / 2
  return [
    { name: 'nw', x: r.x, y: r.y },
    { name: 'n', x: cx, y: r.y },
    { name: 'ne', x: r.x + r.w, y: r.y },
    { name: 'e', x: r.x + r.w, y: cy },
    { name: 'se', x: r.x + r.w, y: r.y + r.h },
    { name: 's', x: cx, y: r.y + r.h },
    { name: 'sw', x: r.x, y: r.y + r.h },
    { name: 'w', x: r.x, y: cy }
  ]
})

// Circle display mapping and handles
const displayCircle = computed(() => {
  const t = selectedTool.value
  if (!t || !t.ROI || !t.ROI.circle) return { cx: 0, cy: 0, r: 0 }
  const sx = imgDisplayWidth.value / (imgNaturalWidth.value || imgDisplayWidth.value || 1)
  const sy = imgDisplayHeight.value / (imgNaturalHeight.value || imgDisplayHeight.value || 1)
  const c = t.ROI.circle
  const scaleAvg = (sx + sy) / 2
  return { cx: (c.cx || 0) * sx, cy: (c.cy || 0) * sy, r: (c.r || 0) * scaleAvg }
})

const circleHandles = computed(() => {
  const c = displayCircle.value
  return [
    { name: 'n', x: c.cx, y: c.cy - c.r },
    { name: 'e', x: c.cx + c.r, y: c.cy },
    { name: 's', x: c.cx, y: c.cy + c.r },
    { name: 'w', x: c.cx - c.r, y: c.cy }
  ]
})

// Ellipse display mapping (sem handles por ora)
const displayEllipse = computed(() => {
  const t = selectedTool.value
  if (!t || !t.ROI || !t.ROI.ellipse) return { cx: 0, cy: 0, rx: 0, ry: 0, angle: 0 }
  const sx = imgDisplayWidth.value / (imgNaturalWidth.value || imgDisplayWidth.value || 1)
  const sy = imgDisplayHeight.value / (imgNaturalHeight.value || imgDisplayHeight.value || 1)
  const e = t.ROI.ellipse
  return { cx: (e.cx || 0) * sx, cy: (e.cy || 0) * sy, rx: (e.rx || 0) * sx, ry: (e.ry || 0) * sy, angle: e.angle || 0 }
})

function toggleOverlay() {
  isOverlayActive.value = !isOverlayActive.value
}

function onRefImageLoad() {
  if (!refImgEl.value) return
  const img = refImgEl.value
  imgNaturalWidth.value = img.naturalWidth || 0
  imgNaturalHeight.value = img.naturalHeight || 0
  // dimensões exibidas
  imgDisplayWidth.value = img.clientWidth || imgNaturalWidth.value
  imgDisplayHeight.value = img.clientHeight || imgNaturalHeight.value
}

function updateDisplaySize() {
  if (!refImgEl.value) return
  imgDisplayWidth.value = refImgEl.value.clientWidth
  imgDisplayHeight.value = refImgEl.value.clientHeight
}

// Atualiza dimensões do overlay quando seleciona ferramenta ou janela redimensiona
watch(selectedTool, () => setTimeout(updateDisplaySize, 0))
if (typeof window !== 'undefined') {
  window.addEventListener('resize', updateDisplaySize)
}

function toImageCoords(px, py) {
  const sx = (imgNaturalWidth.value || imgDisplayWidth.value || 1) / (imgDisplayWidth.value || 1)
  const sy = (imgNaturalHeight.value || imgDisplayHeight.value || 1) / (imgDisplayHeight.value || 1)
  return { x: Math.round(px * sx), y: Math.round(py * sy) }
}

function clampROI(roi) {
  const maxW = imgNaturalWidth.value || 0
  const maxH = imgNaturalHeight.value || 0
  const x = Math.max(0, Math.min(maxW, roi.x))
  const y = Math.max(0, Math.min(maxH, roi.y))
  const w = Math.max(0, Math.min(maxW - x, roi.w))
  const h = Math.max(0, Math.min(maxH - y, roi.h))
  return { x, y, w, h }
}

function setRectROI(x, y, w, h) {
  const t = selectedTool.value
  if (!t) return
  if (!t.ROI) t.ROI = {}
  t.ROI.shape = 'rect'
  t.ROI.rect = clampROI({ x, y, w, h })
  // remover campos legados para não confundir select
  delete t.ROI.x; delete t.ROI.y; delete t.ROI.w; delete t.ROI.h
}

function onOverlayMouseDown(e) {
  if (!isOverlayActive.value) return
  if (!selectedTool.value) return
  const rect = e.currentTarget.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top
  // inicia desenho conforme forma
  if (currentShape.value === 'rect') {
    interaction.value = { mode: 'drawing', startX: x, startY: y, baseRect: null, handle: '' }
  } else if (currentShape.value === 'circle') {
    interaction.value = { mode: 'drawing_circle', startX: x, startY: y, baseRect: null, handle: '' }
    const cImg = toImageCoords(x, y)
    circleROI.value = { cx: cImg.x, cy: cImg.y, r: 1 }
  } else if (currentShape.value === 'ellipse') {
    interaction.value = { mode: 'drawing_ellipse', startX: x, startY: y, baseRect: null, handle: '' }
    const cImg = toImageCoords(x, y)
    ellipseROI.value = { cx: cImg.x, cy: cImg.y, rx: 1, ry: 1, angle: ellipseROI.value.angle || 0 }
  }
  window.addEventListener('mousemove', onMouseMove)
  window.addEventListener('mouseup', onMouseUp)
}

function startMove(e) {
  if (!isOverlayActive.value) return
  const rect = e.currentTarget.ownerSVGElement.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top
  if (currentShape.value === 'circle') {
    interaction.value = { mode: 'moving_circle', startX: x, startY: y, baseCircle: { ...displayCircle.value }, handle: '' }
  } else if (currentShape.value === 'ellipse') {
    interaction.value = { mode: 'moving_ellipse', startX: x, startY: y, baseEllipse: { ...displayEllipse.value }, handle: '' }
  } else {
    interaction.value = { mode: 'moving', startX: x, startY: y, baseRect: { ...displayRect.value }, handle: '' }
  }
  window.addEventListener('mousemove', onMouseMove)
  window.addEventListener('mouseup', onMouseUp)
}

function startResize(handleName, e) {
  if (!isOverlayActive.value) return
  const rect = e.currentTarget.ownerSVGElement.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top
  if (currentShape.value === 'circle') {
    interaction.value = { mode: 'resizing_circle', startX: x, startY: y, baseCircle: { ...displayCircle.value }, handle: handleName }
  } else if (currentShape.value === 'ellipse') {
    // futura implementação: resizing_ellipse; por enquanto permite mover somente
    interaction.value = { mode: 'resizing', startX: x, startY: y, baseRect: { ...displayRect.value }, handle: handleName }
  } else {
    interaction.value = { mode: 'resizing', startX: x, startY: y, baseRect: { ...displayRect.value }, handle: handleName }
  }
  window.addEventListener('mousemove', onMouseMove)
  window.addEventListener('mouseup', onMouseUp)
}

function onMouseMove(e) {
  if (!selectedTool.value) return
  const svg = refImgEl.value ? refImgEl.value.nextElementSibling : null
  if (!svg) return
  const rect = svg.getBoundingClientRect()
  const x = Math.max(0, Math.min(imgDisplayWidth.value, e.clientX - rect.left))
  const y = Math.max(0, Math.min(imgDisplayHeight.value, e.clientY - rect.top))

  if (interaction.value.mode === 'drawing') {
    const dx = x - interaction.value.startX
    const dy = y - interaction.value.startY
    const rx = Math.min(interaction.value.startX, x)
    const ry = Math.min(interaction.value.startY, y)
    const rw = Math.abs(dx)
    const rh = Math.abs(dy)
    const imgRect = toImageCoords(rx, ry)
    const imgSize = toImageCoords(rw, rh)
    setRectROI(imgRect.x, imgRect.y, imgSize.x, imgSize.y)
  } else if (interaction.value.mode === 'drawing_circle') {
    const dx = x - interaction.value.startX
    const dy = y - interaction.value.startY
    const dist = Math.sqrt(dx*dx + dy*dy)
    const s = ( (imgNaturalWidth.value || imgDisplayWidth.value || 1) / (imgDisplayWidth.value || 1) + (imgNaturalHeight.value || imgDisplayHeight.value || 1) / (imgDisplayHeight.value || 1) ) / 2
    const rImg = Math.round(dist * s)
    circleROI.value = { ...circleROI.value, r: rImg }
  } else if (interaction.value.mode === 'drawing_ellipse') {
    const dx = Math.abs(x - interaction.value.startX)
    const dy = Math.abs(y - interaction.value.startY)
    const toImg = toImageCoords(dx, dy)
    ellipseROI.value = { ...ellipseROI.value, rx: toImg.x, ry: toImg.y, angle: ellipseROI.value.angle || 0 }
  } else if (interaction.value.mode === 'moving') {
    const dx = x - interaction.value.startX
    const dy = y - interaction.value.startY
    const base = interaction.value.baseRect
    const imgRect = toImageCoords(base.x + dx, base.y + dy)
    const imgSize = toImageCoords(base.w, base.h)
    setRectROI(imgRect.x, imgRect.y, imgSize.x, imgSize.y)
  } else if (interaction.value.mode === 'moving_circle') {
    const dx = x - interaction.value.startX
    const dy = y - interaction.value.startY
    const base = interaction.value.baseCircle
    const newCenter = toImageCoords(base.cx + dx, base.cy + dy)
    circleROI.value = { ...circleROI.value, cx: newCenter.x, cy: newCenter.y }
  } else if (interaction.value.mode === 'moving_ellipse') {
    const dx = x - interaction.value.startX
    const dy = y - interaction.value.startY
    const base = interaction.value.baseEllipse
    const newCenter = toImageCoords(base.cx + dx, base.cy + dy)
    ellipseROI.value = { ...ellipseROI.value, cx: newCenter.x, cy: newCenter.y }
  } else if (interaction.value.mode === 'resizing') {
    const base = interaction.value.baseRect
    let left = base.x
    let top = base.y
    let right = base.x + base.w
    let bottom = base.y + base.h
    if (interaction.value.handle.includes('w')) left = x
    if (interaction.value.handle.includes('e')) right = x
    if (interaction.value.handle.includes('n')) top = y
    if (interaction.value.handle.includes('s')) bottom = y
    // normaliza
    const nx = Math.min(left, right)
    const ny = Math.min(top, bottom)
    const nw = Math.abs(right - left)
    const nh = Math.abs(bottom - top)
    const imgRect = toImageCoords(nx, ny)
    const imgSize = toImageCoords(nw, nh)
    setRectROI(imgRect.x, imgRect.y, imgSize.x, imgSize.y)
  } else if (interaction.value.mode === 'resizing_circle') {
    const base = interaction.value.baseCircle
    const cx = base.cx
    const cy = base.cy
    const dx = x - cx
    const dy = y - cy
    const dist = Math.sqrt(dx*dx + dy*dy)
    const sx = (imgNaturalWidth.value || imgDisplayWidth.value || 1) / (imgDisplayWidth.value || 1)
    const sy = (imgNaturalHeight.value || imgDisplayHeight.value || 1) / (imgDisplayHeight.value || 1)
    const s = (sx + sy) / 2
    const rImg = Math.round(dist * s)
    circleROI.value = { ...circleROI.value, r: rImg }
  }
}

function onMouseUp() {
  interaction.value = { mode: 'idle', startX: 0, startY: 0, baseRect: null, handle: '' }
  window.removeEventListener('mousemove', onMouseMove)
  window.removeEventListener('mouseup', onMouseUp)
}
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

const shapeOptions = [
  { value: 'rect', text: 'Retângulo' },
  { value: 'circle', text: 'Círculo' },
  { value: 'ellipse', text: 'Elipse' }
]

function normalizeROIForSave(roi) {
  if (!roi || typeof roi !== 'object') return {}
  const out = { shape: roi.shape || undefined }
  if (roi.shape === 'rect' || (!roi.shape && 'x' in roi && 'y' in roi && 'w' in roi && 'h' in roi)) {
    const r = roi.rect || roi
    out.shape = 'rect'
    out.rect = { x: Number(r.x)||0, y: Number(r.y)||0, w: Number(r.w)||0, h: Number(r.h)||0 }
  } else if (roi.shape === 'circle' && roi.circle) {
    out.shape = 'circle'
    out.circle = { cx: Number(roi.circle.cx)||0, cy: Number(roi.circle.cy)||0, r: Number(roi.circle.r)||0 }
  } else if (roi.shape === 'ellipse' && roi.ellipse) {
    out.shape = 'ellipse'
    out.ellipse = { cx: Number(roi.ellipse.cx)||0, cy: Number(roi.ellipse.cy)||0, rx: Number(roi.ellipse.rx)||0, ry: Number(roi.ellipse.ry)||0, angle: Number(roi.ellipse.angle)||0 }
  }
  return out
}

function goBack() {
  router.push('/inspections')
}

function addTool(type) {
  const idx = toolsItems.value.length
  const base = { order_index: idx, name: `${type}_${idx + 1}`, type, inspec_pass_fail: false }
  const roiFull = { shape: 'rect', rect: { x: 0, y: 0, w: 752, h: 480 } }
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

function duplicateTool(index) {
  const src = toolsItems.value[index]
  if (!src) return
  const clone = JSON.parse(JSON.stringify(src))
  // Normaliza ROI para o novo padrão
  clone.ROI = normalizeROIForSave(clone.ROI)
  // Ajusta nome e ordem
  const nextIndex = toolsItems.value.length
  clone.order_index = nextIndex
  clone.name = `${clone.type}_${nextIndex + 1}`
  toolsItems.value.push(clone)
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
    selectedVmId.value = data.vm?.id ? String(data.vm.id) : ''
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
      vm_id: selectedVmId.value ? Number(selectedVmId.value) : null,
      tools: toolsItems.value.map(t => ({
        order_index: t.order_index,
        name: t.name,
        type: t.type,
        ROI: normalizeROIForSave(t.ROI),
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
  const preview = {
    tools: toolsItems.value.map(t => ({
      order_index: t.order_index,
      name: t.name,
      type: t.type,
      ROI: normalizeROIForSave(t.ROI),
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
  jsonPreview.value = JSON.stringify(preview, null, 2)
  showJsonArea.value = true
}

async function updateVM() {
  try {
    saving.value = true
    const payload = { vm_id: selectedVmId.value ? Number(selectedVmId.value) : null, tools: toolsItems.value.map(t => ({
      order_index: t.order_index,
      name: t.name,
      type: t.type,
      ROI: normalizeROIForSave(t.ROI),
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

onMounted(() => {
  load()
  // atualiza tamanho do overlay após imagem carregar
  setTimeout(updateDisplaySize, 0)
  // Carrega lista simples de VMs para associação
  ;(async () => {
    try {
      const r = await apiFetch('/api/vms')
      const j = await r.json()
      vmOptions.value = (j.vms || []).map(vm => ({ value: String(vm.id), text: vm.name || vm.machine_id || `VM ${vm.id}` }))
      vmOptions.value.unshift({ value: '', text: '— Não associar —' })
    } catch {
      vmOptions.value = [{ value: '', text: '—' }]
    }
  })()
})

function onRowClicked(item, index) {
  selectedIdx.value = index
}

// selectedTool já declarado acima
</script>

<style scoped>
.bg-secondary {
  background: linear-gradient(135deg, #6c757d 0%, #5c636a 100%) !important;
}
.ref-image-panel {
  position: relative;
}
.ref-image-wrapper {
  position: relative;
  display: inline-block;
}
.ref-image-wrapper img {
  max-width: 100%;
  height: auto;
  display: block;
}
.roi-overlay {
  position: absolute;
  top: 0;
  left: 0;
  pointer-events: auto;
}
.roi-rect {
  fill: rgba(0, 123, 255, 0.15);
  stroke: #0d6efd;
  stroke-width: 2;
  cursor: move;
}
.roi-handle {
  fill: #fff;
  stroke: #0d6efd;
  stroke-width: 2;
  cursor: pointer;
}
</style>


