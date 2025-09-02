# analyticLens

Plataforma low-code/no-code para configurar inspeções visuais. O usuário monta pipelines visuais (ex.: câmera → pré‑processo → ferramenta → regra → saída) e executa no backend com visão computacional.

## 🚀 **Estado Atual do Projeto**

O projeto está em desenvolvimento ativo com as seguintes funcionalidades implementadas:

### ✅ **Funcionalidades Implementadas**
- **Sistema de Autenticação**: Login/logout com sessões Django
- **Frontend Vue.js**: Interface moderna e responsiva
- **Backend Django**: APIs REST funcionais
- **Vision Machine**: Servidor Flask para processamento de visão computacional
- **Sistema de Tools**: Ferramentas modulares para inspeção visual
- **Comandos da API**: Gerenciamento dinâmico de tools via API
- **Sistema de Testes**: Testes automatizados com backup/restauração

### 🔧 **Sistema de Tools**
O projeto inclui um sistema completo de ferramentas de visão computacional:

- **GrayscaleTool**: Conversão para escala de cinza com múltiplos métodos
- **BlobTool**: Detecção e análise de objetos em imagens
- **MathTool**: Operações matemáticas sobre resultados de outras tools
- **Pipeline Otimizado**: Cache de imagens e processamento sequencial
- **API de Gerenciamento**: Comandos `config_tool` e `delete_tool` para controle dinâmico

> 📖 **Para informações detalhadas sobre as tools, consulte o [TOOLS_README.md](vision_machine/TOOLS_README.md)**

## Principais recursos

- Montagem visual de pipelines (drag & drop)
- Ferramentas de visão modulares (ex.: Blob counter, threshold, morfologia)
- Validação de configurações e contratos de API
- Execução local/sob demanda com retorno de métricas e overlays
- **Vision Machine**: Servidor dedicado para processamento de visão computacional
- **Sistema de Tools**: Ferramentas modulares e configuráveis via JSON
- **Comandos da API**: Gerenciamento dinâmico de tools em tempo real

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

### Vision Machine

- Flask (servidor web para processamento de visão)
- OpenCV (processamento de imagens)
- NumPy (computação numérica)
- Flask-SocketIO (WebSocket para comunicação em tempo real)
- Sistema de ferramentas modulares (grayscale, blob, math)

## Arquitetura

- API prefixada em `/api/` (DRF)
- SPA (Vue) em modo history; servidor retorna `index.html` para todas as rotas que não sejam `api/`, `admin/`, `static/`, `media/`
- Dev desacoplado: Vite em `5173`, Django em `8000`, Vision Machine em `5000`
- Produção acoplada: mesmo domínio para front e API, com fallback do SPA
- **Vision Machine**: Servidor separado para processamento intensivo de visão computacional

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
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser  # crie um usuário admin
python manage.py runserver
```

### Vision Machine

Servidor Flask para processamento de visão computacional.

```bash
cd vision_machine
pip install -r requirements.txt
python vm.py --machine-id vm_001 --django-url http://localhost:8000
```

**Endpoints da Vision Machine:**
- `/api/control` - Comandos de controle (config_tool, delete_tool, etc.)
- `/api/inspection_config` - Configuração das tools
- `/api/source_config` - Configuração da fonte de imagens
- `/api/trigger_config` - Configuração do trigger
- WebSocket para comunicação em tempo real

**Fontes de imagem suportadas (Vision Machine):** `pasta`, `camera`, `camera_IP`, `picamera2`.

Exemplo (Raspberry Pi - Picamera2):
```bash
curl -X PUT http://<IP_DA_VM>:5000/api/source_config \
  -H "Content-Type: application/json" \
  -d '{"type":"picamera2","resolution":[1280,720]}'
```

### Frontend (Vue 3 + Vite)

Já está configurado no diretório `frontend/`.

```bash
cd frontend
npm i
npm run dev
```

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
│  ├─ static/js/         # arquivos JavaScript
│  ├─ static/css/        # arquivos CSS e fontes
│  └─ static/img/        # imagens e ícones
│  ├─ settings.py        # configuração Django
│  └─ urls.py            # roteamento principal
├─ user/                 # app de autenticação (User custom + endpoints /api/auth/*)
├─ vision_machine/       # Servidor Flask para visão computacional
│  ├─ vm.py              # Servidor principal da Vision Machine
│  ├─ inspection_processor.py  # Processador de ferramentas
│  ├─ tools/             # Ferramentas de visão computacional
│  ├─ test_tools.py      # Sistema de testes automatizados
│  ├─ TOOLS_README.md    # Documentação completa das tools
│  ├─ vm_config.json     # Configuração das tools
│  └─ requirements.txt   # Dependências da Vision Machine
├─ modelagem/            # Documentação UML e modelagem do sistema
│  ├─ diagrama_classes_analyticLens.puml
│  ├─ diagrama_sequencia_analyticLens.puml
│  ├─ diagrama_atividades_analyticLens.puml
│  ├─ diagrama_componentes_analyticLens.puml
│  ├─ diagrama_casos_uso_analyticLens.puml
│  └─ proposta de tecnologias.txt
├─ manage.py             # Django CLI
├─ db.sqlite3            # banco SQLite (gerado)
├─ requirements.txt      # dependências Python do projeto principal
├─ .gitignore            # arquivos ignorados pelo Git
├─ .gitattributes        # configurações Git
└─ README.md             # este arquivo
```

## Sistema de Tools

### 🛠️ **Ferramentas Disponíveis**

- **GrayscaleTool**: Conversão para escala de cinza (luminance, average, weighted)
- **BlobTool**: Detecção de objetos com testes de área e contagem
- **MathTool**: Operações matemáticas e fórmulas customizadas

### 🎮 **Comandos da API**

- **`config_tool`**: Atualizar ou adicionar tools
- **`delete_tool`**: Remover tools pelo ID
- **Gerenciamento dinâmico**: Sem necessidade de reiniciar a VM

### 🧪 **Sistema de Testes**

- **Teste automatizado**: `python test_tools.py`
- **Backup automático**: Preserva configuração original
- **Restauração garantida**: Rollback automático após testes

> 📖 **Para configuração detalhada, comandos da API e explicação dos parâmetros, consulte o [TOOLS_README.md](vision_machine/TOOLS_README.md)**

## Build e deploy do front via Django (SPA)

- Dev:
  - Backend: `python manage.py runserver`
  - Frontend: `cd frontend && npm run dev`
  - Vision Machine: `cd vision_machine && python vm.py`
- Produção/local:
  - `cd frontend && npm run build` (gera `dist/` e organiza em `server/static/js/`, `css/`, `img/` e reescreve `server/templates/index.html`)
  - `python manage.py runserver`
  - `cd vision_machine && python vm.py`

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
- **`TOOLS_README.md`**: Documentação completa do sistema de tools
- **Todos os diagramas testados** e funcionando no PlantUML Online

## Roadmap (incremental)

### ✅ **Implementado**
- Sistema de autenticação com Django
- Frontend Vue.js funcional
- Vision Machine com sistema de tools
- Comandos da API para gerenciamento de tools
- Sistema de testes automatizados

### 🚧 **Em Desenvolvimento**
- Interface visual para configuração de tools
- Pipeline builder com drag & drop
- Integração frontend ↔ Vision Machine

### 🔮 **Próximos Passos**
- Ferramentas adicionais: Edge Detection, Color Analysis, Pattern Matching
- Pipelines: execução síncrona (MVP) → assíncrona (jobs) quando necessário
- Streaming: eventos via WebSocket; frames JPEG no MVP; evoluir para WebRTC/RTSP
- Sistema de plugins para ferramentas customizadas

## Scripts úteis

### Backend
```bash
python manage.py runserver
python manage.py migrate
python manage.py createsuperuser
```

### Frontend
```bash
cd frontend
npm run dev
npm run build
```

### Vision Machine
```bash
cd vision_machine
python vm.py --machine-id vm_001 --django-url http://localhost:8000
python test_tools.py  # Executar testes das tools
```

## 🆘 **Suporte e Documentação**

- **README Geral**: Este arquivo (visão geral do projeto)
- **TOOLS_README.md**: Documentação completa do sistema de tools
- **Modelagem UML**: Diagramas na pasta `modelagem/`
- **Testes**: Sistema automatizado em `vision_machine/test_tools.py`

## 🤝 **Contribuindo**

1. Clone o repositório
2. Configure o ambiente de desenvolvimento
3. Execute os testes: `python vision_machine/test_tools.py`
4. Faça suas alterações
5. Execute os testes novamente
6. Envie um pull request

---

**analyticLens** - Plataforma de visão computacional low-code/no-code para inspeções industriais.


