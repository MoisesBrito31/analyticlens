import { rmSync, mkdirSync, cpSync, existsSync, readFileSync, writeFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, resolve } from 'node:path'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

const projectRoot = resolve(__dirname, '..')
const distDir = resolve(projectRoot, 'dist')
// destino dentro do Django: server/static/frontend
const djangoStatic = resolve(projectRoot, '..', 'server', 'static', 'frontend')
const djangoTemplatesDir = resolve(projectRoot, '..', 'server', 'templates')
const djangoIndex = resolve(djangoTemplatesDir, 'index.html')

if (!existsSync(distDir)) {
  throw new Error('Dist não encontrado. Execute "npm run build" primeiro.')
}

// Limpa destino
rmSync(djangoStatic, { recursive: true, force: true })
mkdirSync(djangoStatic, { recursive: true })

// Copia build do Vite para o Django (inclui assets e arquivos públicos)
cpSync(distDir, djangoStatic, { recursive: true })

// Reescreve o index.html para apontar para /static/frontend/assets
const indexPath = resolve(distDir, 'index.html')
try {
  const html = readFileSync(indexPath, 'utf-8')
  // Ajusta referências a assets para o prefixo de estáticos do Django
  let rewritten = html
    .replaceAll(/(href|src)=["']\/?assets\//g, '$1="/static/frontend/assets/')
    .replaceAll(/(href|src)=["']assets\//g, '$1="/static/frontend/assets/')
    .replaceAll('href="/favicon.ico"', 'href="/static/frontend/favicon.ico"')

  mkdirSync(djangoTemplatesDir, { recursive: true })
  writeFileSync(djangoIndex, rewritten, 'utf-8')
  console.log('index.html reescrito em', djangoIndex)
} catch (e) {
  console.warn('Aviso: não foi possível reescrever index.html:', e.message)
}

console.log('Build copiado para', djangoStatic)


