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

Já está configurado no projeto.

```bash
python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell
pip install --upgrade pip
pip install django djangorestframework django-cors-headers numpy opencv-python-headless pillow
python manage.py migrate
python manage.py createsuperuser  # crie um usuário admin
python manage.py runserver
```

Pontos importantes já aplicados no código:

- `INSTALLED_APPS`: `rest_framework`, `corsheaders`, `api`, `user`
- `MIDDLEWARE`: `corsheaders.middleware.CorsMiddleware`
- CORS/CSRF dev: `http://localhost:5173`
- `AUTH_USER_MODEL = 'user.User'` (modelo customizado)
- `TEMPLATES.DIRS = server/templates` e `STATICFILES_DIRS = server/static`

Rotas principais do backend:

- `/api/` → DRF apps
- `/api/auth/csrf` | `/api/auth/login` | `/api/auth/logout` | `/api/auth/me` (sessão)
- Fallback SPA: qualquer rota não‑API cai em `templates/index.html`

Endpoints iniciais (sugestão):

- `GET /api/ping` → healthcheck
- `GET /api/tools` → lista ferramentas disponíveis e schemas de parâmetros
- `POST /api/tools/{tool_id}/run` → executa uma ferramenta (ex.: blob) sobre uma imagem

### Frontend (Vue 3 + Vite)

Já está configurado no diretório `frontend/`.

```bash
cd frontend
npm i
npm run dev
```

Configurações relevantes já no código:

- `vite.config.js`: proxy `/api -> http://localhost:8000` e build com `manifest`
- `src/main.js`: registra BootstrapVue 3 e FormKit (com temas)
- `src/utils/http.js`: wrapper `fetch` que inclui `credentials: 'include'` e injeta `X-CSRFToken` automaticamente em requisições não‑GET
- Autenticação no front:
  - Store `src/stores/auth.js` com `login`, `logout`, `loadMe`
  - `src/views/LoginView.vue`
  - Guard no `vue-router` exigindo login (`meta.requiresAuth`)

## Estrutura atual do repositório

```text
analyticLens/
├─ .venv/                # ambiente virtual Python
├─ .git/                 # repositório Git
├─ api/                  # app DRF (endpoints básicos, ex.: /api/ping)
├─ frontend/             # Vue 3 + Vite (SPA)
│  ├─ src/
│  │  ├─ assets/         # CSS, imagens
│  │  ├─ components/     # componentes Vue
│  │  ├─ router/         # vue-router
│  │  ├─ stores/         # pinia (auth, counter)
│  │  ├─ utils/          # http.js (wrapper fetch)
│  │  └─ views/          # páginas (Home, About, Login)
│  ├─ scripts/           # copy-dist-to-django.mjs
│  ├─ dist/              # build do Vite (gerado)
│  ├─ node_modules/      # dependências Node
│  ├─ package.json       # dependências e scripts
│  └─ vite.config.js     # configuração Vite + proxy
├─ server/               # Django project
│  ├─ templates/         # index.html do SPA (reescrito no build)
│  ├─ static/frontend/   # bundles do Vite copiados no build
│  ├─ settings.py        # configuração Django
│  └─ urls.py            # roteamento principal
├─ user/                 # app de autenticação (User custom + endpoints /api/auth/*)
├─ modelagem/            # Documentação UML e modelagem do sistema
│  ├─ diagrama_classes_analyticLens.puml
│  ├─ diagrama_sequencia_analyticLens.puml
│  ├─ diagrama_atividades_analyticLens.puml
│  ├─ diagrama_componentes_analyticLens.puml
│  ├─ diagrama_casos_uso_analyticLens.puml
│  └─ proposta de tecnologias.txt
├─ manage.py             # Django CLI
├─ db.sqlite3            # banco SQLite (gerado)
├─ .gitignore            # arquivos ignorados pelo Git
├─ .gitattributes        # configurações Git
└─ README.md             # este arquivo
```

**Nota**: Os apps Django (`api/` e `user/`) ficam na raiz do projeto, não dentro de `server/`. O `server/` contém apenas configurações do projeto Django.

## Build e deploy do front via Django (SPA)

- Dev:
  - Backend: `python manage.py runserver`
  - Frontend: `cd frontend && npm run dev`
- Produção/local:
  - `cd frontend && npm run build` (gera `dist/` e copia para `server/static/frontend/` e reescreve `server/templates/index.html`)
  - `python manage.py runserver`

## Modelagem do Sistema

### 📊 Diagramas UML

O projeto inclui uma documentação completa de modelagem UML na pasta `modelagem/`:

#### **🏗️ Diagrama de Classes**
- **Arquivo**: `diagrama_classes_analyticLens.puml`
- **Propósito**: Estrutura do sistema, modelos de dados, relacionamentos entre entidades
- **Cobertura**: Django models, Vue components, Pinia stores, Computer Vision tools

#### **🔄 Diagrama de Sequência**
- **Arquivo**: `diagrama_sequencia_analyticLens.puml`
- **Propósito**: Fluxo de execução das inspeções, interação entre componentes
- **Cobertura**: Pipeline de execução, comunicação Frontend ↔ Backend, processamento de imagens

#### **⚙️ Diagrama de Atividades**
- **Arquivo**: `diagrama_atividades_analyticLens.puml`
- **Propósito**: Workflow do pipeline de inspeção, decisões e processos paralelos
- **Cobertura**: Fluxo completo desde upload até resultado, validações e loops

#### **🏛️ Diagrama de Componentes**
- **Arquivo**: `diagrama_componentes_analyticLens.puml`
- **Propósito**: Arquitetura do sistema, componentes principais e suas interações
- **Cobertura**: Frontend Vue.js, Backend Django, Computer Vision Engine, Database

#### **🎭 Diagrama de Casos de Uso**
- **Arquivo**: `diagrama_casos_uso_analyticLens.puml`
- **Propósito**: Funcionalidades do sistema, atores e suas responsabilidades
- **Cobertura**: 8 pacotes de funcionalidades, 50+ casos de uso, relacionamentos include/extend

### 🎨 Como Visualizar

Os diagramas estão em formato PlantUML (`.puml`) e podem ser visualizados:

1. **Online**: https://www.plantuml.com/plantuml/uml/
2. **VS Code**: Extensão "PlantUML" (jebbs.plantuml)
3. **Desktop**: PlantUML.jar com Java instalado

### 📋 Documentação Adicional

- **`proposta de tecnologias.txt`**: Análise inicial das tecnologias escolhidas
- **Todos os diagramas testados** e funcionando no PlantUML Online

## Roadmap (incremental)

- Ferramenta inicial: Blob (contagem por intervalo de intensidade/cor em ROI)
- Tools: threshold, morfologia (erode/dilate/open/close), contornos, ROI, medição
- Pipelines: execução síncrona (MVP) → assíncrona (jobs) quando necessário
- Autenticação: sessão Django (já implementada no MVP) ou JWT (futuro)
- Streaming: eventos via WebSocket; frames JPEG no MVP; evoluir para WebRTC/RTSP

## Scripts úteis

- Backend:
  - `python manage.py runserver`
  - `python manage.py migrate`
- Frontend:
  - `npm run dev`
  - `npm run build`


