# Setup do Frontend - AnalyticLens

## 📋 Pré-requisitos

- **Node.js**: Versão 20.19.0 ou superior (recomendado: 20.x LTS)
- **npm**: Versão 9.0.0 ou superior

## 🚀 Instalação Rápida

### 1. Verificar versões
```bash
node --version  # Deve ser >= 20.19.0
npm --version   # Deve ser >= 9.0.0
```

### 2. Instalar dependências
```bash
npm install
```

### 3. Executar em desenvolvimento
```bash
npm run dev
```

## 🔧 Scripts Disponíveis

- `npm run dev` - Executa em modo desenvolvimento
- `npm run build` - Build para produção
- `npm run preview` - Preview do build
- `npm run lint` - Lint e correção automática
- `npm run setup` - Setup completo (install + verificação)
- `npm run clean` - Limpa e reinstala tudo

## ⚠️ Solução de Problemas

### Erro de versão do Node.js
```bash
# Se estiver com Node.js < 20.19.0, atualize:
# Windows: Baixe do nodejs.org
# Linux/Mac: Use nvm
nvm install 20.19.0
nvm use 20.19.0
```

### Erro de dependências
```bash
# Limpar e reinstalar
npm run clean

# Ou manualmente:
rm -rf node_modules package-lock.json
npm install
```

### Erro de @popperjs/core
```bash
# Instalar explicitamente
npm install @popperjs/core@^2.11.8
```

## 🌐 Acesso

- **Desenvolvimento**: http://localhost:5173/
- **Vue DevTools**: http://localhost:5173/__devtools__/

## 📁 Estrutura

```
frontend/
├── src/           # Código fonte
├── public/        # Arquivos estáticos
├── package.json   # Dependências e scripts
├── .nvmrc        # Versão do Node.js
└── README_SETUP.md # Este arquivo
```

## 🔄 Para Novos Clones

1. Clone o repositório
2. `cd frontend`
3. `npm run setup`
4. `npm run dev`

## 📞 Suporte

Se encontrar problemas:
1. Verifique as versões do Node.js e npm
2. Execute `npm run clean`
3. Consulte este README
4. Verifique se está na pasta correta (`frontend/`)
