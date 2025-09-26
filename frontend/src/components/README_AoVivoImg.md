# AoVivoImg — Guia de Uso e Arquitetura (após refatoração)

Este documento descreve o componente `AoVivoImg.vue` depois da refatoração, incluindo os componentes auxiliares, props, eventos, fluxo de dados e exemplos de integração na tela de edição online.

## Visão geral

O `AoVivoImg` é um orquestrador de UI para visualizar frames ao vivo, sobrepor informações de inspeção (ROI, blobs, contornos, etc.), exibir uma linha do tempo de resultados (pass/fail), métricas correntes e permitir editar parâmetros das ferramentas (tools) quando em modo de edição.

Ele foi modularizado para manter responsabilidade clara, melhor legibilidade e manutenção.

## Arquitetura (componentes e composables)

- `AoVivoImg.vue` (orquestrador)
  - Recebe os dados (frame, metrics, results/tools) e concentra o estado de seleção de tool.
  - Emite eventos para o pai (seleção de tool e atualização de parâmetros).
- `RoiOverlay.vue`
  - Renderiza, em SVG, o ROI (retângulo, círculo, elipse) e elementos de análise dos blobs (centróides, caixas e contornos).
  - Suporta edição interativa do ROI: arrasto para mover e handles para redimensionar (retângulo/círculo/elipse). Pressione Shift para ajuste fino. Opções: `dragGain` (ganho), `snapToGrid` e `gridStep`.
- `TimelineDots.vue`
  - Mostra 60 marcadores (configurável) representando pass/fail/unknown dos últimos frames.
- `MetricsPanel.vue`
  - Exibe métricas resumidas: aprovados, reprovados, tempo, frame.
- `ToolParamsPanel.vue`
  - Escolhe dinamicamente qual subpainel de parâmetros renderizar conforme o tipo da tool.
  - Subcomponentes em `components/tool-params/`: `BlobParams.vue`, `GrayscaleParams.vue`, `BlurParams.vue`, `ThresholdParams.vue`, `MorphologyParams.vue`, `MathParams.vue`.
- `ToolCardsPanel.vue`
  - Lista de ferramentas (cards) com seleção e suporte a drag-and-drop para reordenar.
- Composables
  - `useToolParams`
    - Fornece `getParam` e `selectedToolType` a partir do item selecionado e da definição da tool.
  - `useLiveSocket` (utilitário)
    - Auxilia conexão e eventos do Socket.IO (usado pela view que hospeda o `AoVivoImg`).

## Props do AoVivoImg

- `binary: ArrayBuffer | Uint8Array | Blob | string | null`
  - Dados do frame atual. Suporta Blob, ArrayBuffer/Uint8Array e base64 string (ou URL/data URL).
- `tools: Array`
  - Lista de configurações das ferramentas (definições). Usada como fallback para metadados quando `results` não estiver populado.
- `toolDefs: Array`
  - Definições de tools (opcional). Usadas para preencher valores padrão ao montar parâmetros quando o item selecionado não traz todos os campos.
- `metrics: Object` (default `{ aprovados: 0, reprovados: 0, time: '', frame: 0 }`)
  - Métricas correntes da inspeção; `frame` é usado para alimentar a timeline.
- `results: Array`
  - Resultado por tool do frame corrente (inclui `pass_fail`, `blobs`, tempos, etc.). Quando presente, é a fonte preferível para exibição.
- `resolution: [width, height]`
  - Resolução usada pelo SVG para posicionar ROI e overlays.
- `mimeType: string` (default `image/jpeg`)
- `alt: string` (default `Frame ao vivo`)
- `fit: string` (default `contain`)
- `ratio: string | number` (default `16/9`)
- `readOnly: boolean` (default `true`)
  - Quando `false`, habilita edição de parâmetros das tools via `ToolParamsPanel`.

## Eventos emitidos

- `select: ({ index, item, roi, pass_fail } | null)`
  - Emitido ao selecionar/deselecionar um card de tool.
- `update-tool-param: ({ index, key, value })`
  - Emitido ao alterar algum parâmetro da tool selecionada. O pai (ex.: `InspectionEditOnlineView`) deve consolidar e enviar o payload para o backend (update_vm) de forma debounced.
  - Quando `key === 'ROI'`, o `value` segue o formato tipado `{ shape: 'rect'|'circle'|'ellipse', rect|circle|ellipse: {...} }`.
  - Reordenação: `key === 'REORDER'` com `value = { from, to, order }`, onde `order` é a nova lista de ids das tools.

## Fluxo de dados (resumo)

1. A view hospedeira (ex.: `InspectionEditOnlineView.vue`) conecta-se ao WebSocket e recebe eventos (`test_result`) da VM.
2. A cada evento, atualiza props do `AoVivoImg` (`binary`, `results`, `metrics`, `resolution`, etc.).
3. O `AoVivoImg`:
   - Converte `binary` em URL de exibição.
   - Seleciona automaticamente a primeira tool na primeira carga.
   - Usa `RoiOverlay` para desenhar ROI e elementos de análise com base em `results`.
   - Atualiza `timelineDots` quando `metrics.frame` muda, gerando `timelineDisplay` (mais recente à esquerda).
4. Quando o usuário altera parâmetros em `ToolParamsPanel`, o `AoVivoImg` emite `update-tool-param` para o pai.
5. A view hospedeira agrega essas mudanças e faz a chamada à API `/api/inspections/{insp_id}/update_vm` (idealmente com debounce e tratamento otimista/rollback).

## Detalhes por seção

### Imagem, overlays e edição de ROI (com Locate/offset)

- O frame é exibido como `<img />` com `object-fit` configurável por `fit`.
- O overlay é um SVG com `viewBox` baseado em `resolution` e desenha:
  - ROI retângulo/círculo/elipse
  - Centrôides dos blobs
  - Caixas (bounding boxes) dos blobs
  - Contornos/polígonos dos blobs
- Edição de ROI: pode ser feita pelo overlay (drag/handles) ou pela aba Parâmetros (campos numéricos). Mudanças refletem imediatamente no overlay e são emitidas ao pai como `update-tool-param` (key `ROI`).
- Locate e offset em tempo real:
  - Quando uma `Locate` anterior tem `apply_transform=true`, o ROI efetivo das tools seguintes é realocado automaticamente pelo offset.
  - A seta (`arrow`) e as bordas (edges) da `Locate` selecionada também exibem o offset aplicado quando a edição de ROI está desabilitada.
  - Toggle “Edição ROI”: quando ligado, o overlay exibe e permite editar o ROI/arrow da configuração (sem offset); quando desligado, exibe o ROI/arrow efetivos (com offset).

### ToolCardsPanel: adicionar, reordenar, duplicar e apagar

- Localização: abaixo da imagem, à esquerda.
- Adicionar tool: card “+” abre modal com tipos disponíveis; ao escolher, o `AoVivoImg` emite `update-tool-param` com `key: 'ADD_TOOL'` e o objeto base da ferramenta. A view hospedeira inclui a tool no fim da lista e chama `update_vm`.
- Reordenar: botão “Reordenar” abre um modal com:
  - Painéis fixos indicando a posição da fila (rótulo “1º, 2º, …” no canto superior direito);
  - Dentro de cada painel, um quadrado menor arrastável representando a tool (nome e tipo);
  - Botões por painel: “×” (apagar) e “⧉” (duplicar). As ações afetam somente a visualização do modal; nada é aplicado até o OK.
  - Durante o arrasto, o item original fica invisível e um ghost segue o cursor.
  - Ao clicar em OK, o componente emite um plano consolidado para composição da lista:
    - `INSPECTION_REORDER` via `update-tool-param` com `value = { orderIndexes, deleteIndexes, composePlan }` onde:
      - `composePlan`: sequência completa da visualização com steps `{ kind: 'orig' | 'dup', index, name, type }`;
      - `deleteIndexes`: índices originais a serem removidos;
      - `orderIndexes`: ordem final referenciando posições dentro de `composePlan`.
- A view hospedeira aplica: primeiro `deleteIndexes`, depois cria cópias profundas para steps `dup` (ajustando `name`), constrói a sequência final conforme `orderIndexes`, reatribui `order_index` e chama `update_vm`.
- Modo somente leitura: quando `readOnly === true`, os botões “Adicionar” e “Reordenar” ficam desativados (visualmente e funcionalmente).

### Timeline

- `TimelineDots` recebe um array (máx. 60) com valores `true` (pass), `false` (fail) ou `null` (indefinido) e renderiza uma grade de pontos.
- A timeline é alimentada pela evolução de `metrics.frame` e o cálculo de `overallPass` (consolida pass/fail das tools no frame corrente).

### Métricas

- `MetricsPanel` exibe valores numéricos/strings diretamente de `metrics`.

### Parâmetros de tools (edição)

- `ToolParamsPanel` seleciona subpainéis conforme o tipo da tool: `blob`, `grayscale`, `blur`, `threshold`, `morphology`, `math`, `locate`.
- Para `blob`, os principais campos expostos:
  - `inspec_pass_fail`, `th_min`, `th_max`, `area_min`, `area_max`
  - `total_area_test`, `blob_count_test`
  - `test_total_area_min`, `test_total_area_max`
  - `test_blob_count_min`, `test_blob_count_max`
  - `contour_chain`, `approx_epsilon_ratio`, `polygon_max_points`
- Todos os subpainéis emitem um evento de mudança normalizado para o `ToolParamsPanel`, que por sua vez emite `update` ao `AoVivoImg`; então o `AoVivoImg` emite `update-tool-param` para o pai.
- Campo Geral → Nome da ferramenta:
  - Editável na aba de Parâmetros; aplica normalização automática: remove acentos, substitui espaços/símbolos por `_`, colapsa underscores e faz trim;
  - Unicidade: nomes duplicados são bloqueados; mensagem de erro em vermelho é exibida e nenhuma atualização é emitida até o nome ficar válido.
- Em modo `readOnly=true`, os campos ficam desabilitados (somente leitura); o `inspec_pass_fail` também aparece em leitura.

#### Parâmetros específicos de Locate (na aba Parâmetros)
- `threshold_mode`, `threshold`, `adaptive_k`, `polaridade`, `edge_select`, `smooth_ksize`, `grad_kernel`
- `apply_transform`: quando true, realoca ROIs subsequentes com base no `offset` calculado
- `rotate`: quando true, inclui rotação no deslocamento
- `reference`: `{x, y, angle_deg}`; botão “Definir referência (usar resultado atual)” faz sync com o resultado corrente
- `arrow`: `{p0, p1}` editável no overlay quando Edição ROI está ligada

### Composables

- `useToolParams`
  - `getParam(key, defVal)`: busca um parâmetro considerando o item selecionado e a definição da tool.
  - `selectedToolType`: tipo normalizado da tool selecionada.
- `useLiveSocket`
  - Facilita conectar/desconectar e reagir a `test_result`/estado de conexão. É recomendado usá-lo na view, não dentro do `AoVivoImg`.

## Exemplo de uso (na view)

```vue
<template>
  <AoVivoImg
    :binary="liveFrame"
    :results="liveTools"
    :tool-defs="liveToolDefs"
    :metrics="metrics"
    :resolution="liveResolution"
    :ratio="liveRatio"
    :read-only="false"
    @select="onSelectTool"
    @update-tool-param="onUpdateToolParam"
  />
</template>

<script setup>
import { ref } from 'vue'
import AoVivoImg from '@/components/AoVivoImg.vue'

const liveFrame = ref(null)
const liveTools = ref([])
const liveToolDefs = ref([])
const liveResolution = ref([1280, 720])
const liveRatio = ref('16/9')
const metrics = ref({ aprovados: 0, reprovados: 0, time: '', frame: 0 })

function onSelectTool(payload) {
  // { index, item, roi, pass_fail } | null
}

function onUpdateToolParam({ index, key, value }) {
  if (key === 'ROI') {
    // persistir ROI da tool index na VM (debounced)
  } else if (key === 'ADD_TOOL') {
    // append e enviar recipe completa
  } else if (key === 'INSPECTION_REORDER') {
    // aplicar deleteIndexes, duplicações de composePlan e orderIndexes; enviar recipe completa
  } else if (key === 'name') {
    // já vem normalizado; garantir unicidade antes de enviar
  } else {
    // outros parâmetros por tool
  }
}
</script>
```

## Boas práticas e performance

- Preferir passar `results` (dados do frame corrente) quando disponível; `tools`/`toolDefs` são usados como fonte de default/definição.
- Debounce das atualizações para a VM quando parâmetros são alterados (evita tempestade de requisições).
- Evite reatividade profunda sobre objetos grandes; prefira `shallowRef` na view hospedeira quando manipular resultados brutos.
- Garanta que `resolution` reflita a base em pixels do frame para o overlay ficar alinhado.

## Estilos

- O `AoVivoImg` controla layout com CSS grid (coluna da imagem e coluna lateral), e classes utilitárias para abas, cards e badges.
- `TimelineDots` e `MetricsPanel` possuem estilos encapsulados (`scoped`).

## Solução de problemas

- Timeline vazia:
  - Verifique se `metrics.frame` está incrementando por frame e se `overallPass` está computando (ao menos null). Sem evolução de frame, a timeline não preenche.
- ROI desenhado fora de posição:
  - Confirme se `resolution` corresponde ao espaço de coordenadas do processamento; `viewBox` usa `resolution` diretamente.
- Parâmetros não aplicando:
  - Valide se o pai está escutando `update-tool-param` e montando o payload para o endpoint `update_vm` (incluindo todos os campos relevantes da tool e `ROI`).

## Roadmap (sugestões)

- Reintroduzir edição interativa do ROI em `RoiOverlay.vue` (desenho e handles), mantendo a lógica isolada.
- Adicionar mini toggle de `Pass/Fail` por tool no card (opcional), quando aplicável.
- Otimizações de render para grandes quantidades de blobs/contornos.
