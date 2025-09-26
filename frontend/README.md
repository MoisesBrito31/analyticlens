# frontend

Aplicação Vue 3 (Vite) do AnalyticLens. Este README descreve setup e destaca componentes principais, incluindo o `AoVivoImg` e integrações com a VM.

## Recommended IDE Setup

[VSCode](https://code.visualstudio.com/) + [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (and disable Vetur).

## Customize configuration

Veja a referência do Vite: https://vite.dev/config/

## Project Setup

```sh
npm install
```

### Compile and Hot-Reload for Development

```sh
npm run dev
```

### Compile and Minify for Production

```sh
npm run build
```

### Lint with [ESLint](https://eslint.org/)

```sh
npm run lint
```

## Componentes Principais

- `src/components/AoVivoImg.vue`
  - Exibe o frame ao vivo, sobrepõe ROI/contornos/centróides e mostra análise por tool.
  - Integração tight com VM via props `results`, `metrics`, `resolution`.
  - Edição interativa de ROI e parâmetros de tool via `ToolParamsPanel`.
  - Suporte a `Locate`: botão Sync da referência, `rotate`, `apply_transform`, e realocação de ROIs subsequentes em tempo real.
- `src/components/RoiOverlay.vue`
  - Overlay SVG com edição drag/handles (retângulo, círculo, elipse) e controle da seta (Locate).
- `src/views/InspectionEditOnlineView.vue`
  - Orquestra o `AoVivoImg`, WebSocket e envio de updates para a VM.
- `src/views/InspectionEditOfflineView.vue`
  - Edição, persistência e preview offline de inspeções; inclui suporte completo aos parâmetros da `Locate` (rotate/reference/arrow/apply_transform).

## Suporte a Locate (Frontend)

- Online (`AoVivoImg`):
  - Toggle “Edição ROI”: quando ligado, o overlay mostra a configuração original (sem offset) e habilita editar ROI/arrow. Quando desligado, mostra o ROI/arrow efetivos (com offset aplicado).
  - Aba Análise: mostra Reference / Result / Offset com duas casas decimais.
  - Botão “Definir referência (usar resultado atual)” sincroniza `reference` com o resultado corrente.
- Offline (`InspectionEditOfflineView`):
  - JSON final inclui todos os campos da Locate: `threshold_mode`, `threshold`, `adaptive_k`, `polaridade`, `edge_select`, `smooth_ksize`, `grad_kernel`, `apply_transform`, `rotate`, `reference`, `arrow`.

Mais detalhes em `src/components/README_AoVivoImg.md`.
