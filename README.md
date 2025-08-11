# analyticLens

Plataforma low-code/no-code para configurar inspeções visuais. O usuário monta pipelines visuais (ex.: câmera → pré‑processo → ferramenta → regra → saída) e executa no backend com visão computacional.

## Principais recursos

- Montagem visual de pipelines (drag & drop)
- Ferramentas de visão modulares (ex.: Blob counter, threshold, morfologia)
- Validação de configurações e contratos de API
- Execução local/sob demanda com retorno de métricas e overlays

## Stack

### Frontend

- Vue 3 + Vite
- Vue Router (rotas públicas/privadas)
- Pinia (estado global)
- BootstrapVue 3 (UI)
- Vue Flow (canvas do builder)
- FormKit (formulários e configuração via schema)
- Zod (validação em runtime)
- ESLint (qualidade de código)
- fetch (HTTP) centralizado em um pequeno wrapper

### Backend

- Django (framework web, ORM, autenticação)
- Django REST Framework (APIs REST)
- django-cors-headers (CORS para dev/externo)
- NumPy (base numérica)
- opencv-python-headless (visão computacional no servidor)
- Pillow (I/O e manipulação simples de imagens)

## Arquitetura

- API prefixada em `/api/` (DRF)
- SPA (Vue) em modo history; servidor retorna `index.html` para todas as rotas que não sejam `api/`, `admin/`, `static/`, `media/`
- Dev desacoplado: Vite em `5173`, Django em `8000` (proxy no Vite para `/api`)
- Produção acoplada: mesmo domínio para front e API, com fallback do SPA

## Começando (ambiente de desenvolvimento)

### Requisitos

- Node 18+ e npm
- Python 3.10+ e pip

### Backend (Django + DRF)

```bash
python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell: . .venv/Scripts/Activate.ps1
pip install --upgrade pip
pip install django djangorestframework django-cors-headers numpy opencv-python-headless pillow

# Se ainda não houver projeto
django-admin startproject server
cd server
python manage.py startapp api
```

Habilite apps e middlewares em `server/settings.py`:

```python
INSTALLED_APPS = [
    # ...
    'rest_framework',
    'corsheaders',
    'api',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    # ... demais middlewares do Django ...
]

# Dev: permitir Vite
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',
]
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:5173',
]
```

URLs com API prefixada e fallback do SPA (quando for servir o build pelo Django):

```python
# server/urls.py
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    # Fallback SPA (em produção, quando o build estiver integrado ao Django)
    re_path(r'^(?!api/|admin/|static/|media/).*$', TemplateView.as_view(template_name='index.html')),
]
```

Endpoints iniciais (sugestão):

- `GET /api/ping` → healthcheck
- `GET /api/tools` → lista ferramentas disponíveis e schemas de parâmetros
- `POST /api/tools/{tool_id}/run` → executa uma ferramenta (ex.: blob) sobre uma imagem

### Frontend (Vue 3 + Vite)

```bash
# Cria projeto com Router, Pinia e ESLint (JavaScript para manter simples)
npm create vue@latest frontend
# selecione: JavaScript, Router=Yes, Pinia=Yes, ESLint=Yes

cd frontend
npm i
npm i bootstrap bootstrap-vue-3
npm i @vue-flow/core @vue-flow/controls @vue-flow/minimap @vue-flow/background
npm i @formkit/vue @formkit/themes
npm i zod
```

`vite.config.ts` com proxy para a API (dev):

```ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: { proxy: { '/api': 'http://localhost:8000' } },
})
```

Importe estilos e registre plugins no `main` do front:

```ts
// src/main.ts
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'

import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue-3/dist/bootstrap-vue-3.css'
import BootstrapVue3 from 'bootstrap-vue-3'

import { plugin as FormKit, defaultConfig } from '@formkit/vue'
import '@formkit/themes/genesis'

createApp(App)
  .use(router)
  .use(createPinia())
  .use(BootstrapVue3)
  .use(FormKit, defaultConfig)
  .mount('#app')
```

Wrapper simples para HTTP com fetch:

```ts
// src/utils/http.ts
export async function apiFetch(input: RequestInfo, init: RequestInit = {}) {
  const headers = new Headers(init.headers)
  if (init.method && init.method !== 'GET' && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }
  const res = await fetch(input, { credentials: 'include', ...init, headers })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res
}
```

## Estrutura sugerida

```text
analyticLens/
├─ backend/ (opcional, se preferir separar)
│
├─ server/               # Django project
│  ├─ api/               # app DRF (endpoints)
│  └─ ...
│
├─ frontend/             # Vue 3 + Vite (SPA)
│  ├─ src/
│  │  ├─ router/         # vue-router
│  │  ├─ stores/         # pinia
│  │  ├─ utils/http.ts   # fetch wrapper
│  │  └─ features/flow/  # Vue Flow + FormKit (builder)
│  └─ ...
└─ README.md
```

## Roadmap (incremental)

- Ferramenta inicial: Blob (contagem por intervalo de intensidade/cor em ROI)
- Tools: threshold, morfologia (erode/dilate/open/close), contornos, ROI, medição
- Pipelines: execução síncrona (MVP) → assíncrona (jobs) quando necessário
- Autenticação: sessão Django (mesmo domínio) ou JWT (separação/SSO)
- Streaming: eventos via WebSocket; frames JPEG no MVP; evoluir para WebRTC/RTSP

## Scripts úteis

- Backend:
  - `python manage.py runserver`
  - `python manage.py migrate`
- Frontend:
  - `npm run dev`
  - `npm run build`

## Licença

Defina a licença conforme a necessidade do projeto (ex.: MIT, Apache-2.0).


