import { rmSync, mkdirSync, cpSync, existsSync, readFileSync, writeFileSync, readdirSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, resolve } from 'node:path'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

const projectRoot = resolve(__dirname, '..')
const distDir = resolve(projectRoot, 'dist')
const srcAssetsDir = resolve(projectRoot, 'src', 'assets')
// destino dentro do Django: server/static (sem pasta frontend)
const djangoStatic = resolve(projectRoot, '..', 'server', 'static')
const djangoTemplatesDir = resolve(projectRoot, '..', 'server', 'templates')
const djangoIndex = resolve(djangoTemplatesDir, 'index.html')

if (!existsSync(distDir)) {
  throw new Error('Dist não encontrado. Execute "npm run build" primeiro.')
}

// Limpa destino e cria estrutura organizada
rmSync(djangoStatic, { recursive: true, force: true })
mkdirSync(djangoStatic, { recursive: true })
mkdirSync(resolve(djangoStatic, 'js'), { recursive: true })
mkdirSync(resolve(djangoStatic, 'css'), { recursive: true })
mkdirSync(resolve(djangoStatic, 'img'), { recursive: true })

// Copia build do Vite para o Django
cpSync(distDir, djangoStatic, { recursive: true })

// Organiza arquivos nas pastas corretas
console.log('🔧 Organizando arquivos por tipo...')

// Move arquivos JS para pasta js
const jsFiles = []
if (existsSync(resolve(djangoStatic, 'assets'))) {
  const files = readdirSync(resolve(djangoStatic, 'assets'))
  jsFiles.push(...files.filter(file => file.endsWith('.js')))
}

for (const jsFile of jsFiles) {
  const sourcePath = resolve(djangoStatic, 'assets', jsFile)
  const destPath = resolve(djangoStatic, 'js', jsFile)
  if (existsSync(sourcePath)) {
    cpSync(sourcePath, destPath)
    rmSync(sourcePath)
    console.log(`✅ JS movido: ${jsFile}`)
  }
}

// Move arquivos CSS para pasta css
const cssFiles = []
if (existsSync(resolve(djangoStatic, 'assets'))) {
  const files = readdirSync(resolve(djangoStatic, 'assets'))
  cssFiles.push(...files.filter(file => file.endsWith('.css')))
}

for (const cssFile of cssFiles) {
  const sourcePath = resolve(djangoStatic, 'assets', cssFile)
  const destPath = resolve(djangoStatic, 'css', cssFile)
  if (existsSync(sourcePath)) {
    cpSync(sourcePath, destPath)
    rmSync(sourcePath)
    console.log(`✅ CSS movido: ${cssFile}`)
  }
}

// Move fontes para pasta css
const fontFiles = []
if (existsSync(resolve(djangoStatic, 'assets'))) {
  const files = readdirSync(resolve(djangoStatic, 'assets'))
  fontFiles.push(...files.filter(file => file.endsWith('.woff') || file.endsWith('.woff2')))
}

for (const fontFile of fontFiles) {
  const sourcePath = resolve(djangoStatic, 'assets', fontFile)
  const destPath = resolve(djangoStatic, 'css', fontFile)
  if (existsSync(sourcePath)) {
    cpSync(sourcePath, destPath)
    rmSync(sourcePath)
    console.log(`✅ Fonte movida: ${fontFile}`)
  }
}

// GARANTIA: Copia fontes do Bootstrap Icons se não foram encontradas
console.log('🔍 Verificando se as fontes do Bootstrap Icons foram copiadas...')
const requiredFonts = ['bootstrap-icons.woff2', 'bootstrap-icons.woff']
const bootstrapIconsFontsDir = resolve(projectRoot, 'node_modules', 'bootstrap-icons', 'font', 'fonts')

for (const fontName of requiredFonts) {
  const destPath = resolve(djangoStatic, 'css', fontName)
  if (!existsSync(destPath)) {
    const srcPath = resolve(bootstrapIconsFontsDir, fontName)
    if (existsSync(srcPath)) {
      cpSync(srcPath, destPath)
      console.log(`✅ Fonte copiada diretamente: ${fontName}`)
    } else {
      console.warn(`⚠️  Fonte não encontrada: ${fontName}`)
    }
  } else {
    console.log(`✅ Fonte já existe: ${fontName}`)
  }
}

// Move imagens para pasta img
const imageFiles = []
if (existsSync(resolve(djangoStatic, 'assets'))) {
  const files = readdirSync(resolve(djangoStatic, 'assets'))
  imageFiles.push(...files.filter(file => file.endsWith('.svg') || file.endsWith('.png') || file.endsWith('.jpg') || file.endsWith('.jpeg') || file.endsWith('.gif')))
}

for (const imageFile of imageFiles) {
  const sourcePath = resolve(djangoStatic, 'assets', imageFile)
  const destPath = resolve(djangoStatic, 'img', imageFile)
  if (existsSync(sourcePath)) {
    cpSync(sourcePath, destPath)
    rmSync(sourcePath)
    console.log(`✅ Imagem movida: ${imageFile}`)
  }
}

// Move arquivos de imagem da raiz para pasta img
const rootImageFiles = []
if (existsSync(djangoStatic)) {
  const files = readdirSync(djangoStatic)
  rootImageFiles.push(...files.filter(file => file.endsWith('.svg') || file.endsWith('.ico')))
}

for (const imageFile of rootImageFiles) {
  const sourcePath = resolve(djangoStatic, imageFile)
  const destPath = resolve(djangoStatic, 'img', imageFile)
  if (existsSync(sourcePath) && !existsSync(destPath)) {
    cpSync(sourcePath, destPath)
    console.log(`✅ Imagem da raiz movida: ${imageFile}`)
  }
}

// GARANTIA: Copia imagens diretamente da pasta src/assets se não foram encontradas
console.log('🔍 Verificando se todas as imagens foram copiadas...')
const requiredImages = ['logo.svg', 'logo-large.svg', 'favicon.svg', 'favicon.ico']

for (const imageName of requiredImages) {
  const destPath = resolve(djangoStatic, 'img', imageName)
  if (!existsSync(destPath)) {
    const srcPath = resolve(srcAssetsDir, imageName)
    if (existsSync(srcPath)) {
      cpSync(srcPath, destPath)
      console.log(`✅ Imagem copiada diretamente: ${imageName}`)
    } else {
      console.warn(`⚠️  Imagem não encontrada: ${imageName}`)
    }
  } else {
    console.log(`✅ Imagem já existe: ${imageName}`)
  }
}

// Reescreve o index.html para apontar para as novas pastas
const indexPath = resolve(distDir, 'index.html')
try {
  const html = readFileSync(indexPath, 'utf-8')
  
  // Ajusta referências para as novas pastas organizadas
  let rewritten = html
    .replaceAll(/href=["']\/favicon\.svg["']/g, 'href="/static/img/favicon.svg"')
    .replaceAll(/href=["']\/favicon\.ico["']/g, 'href="/static/img/favicon.ico"')
    .replaceAll(/src=["']\/assets\/([^"']*\.js)["']/g, 'src="/static/js/$1"')
    .replaceAll(/href=["']\/assets\/([^"']*\.css)["']/g, 'href="/static/css/$1"')
    
    // CORREÇÕES ESPECÍFICAS PARA IMAGENS SVG NO HTML
    .replaceAll(/src=["']\/assets\/([^"']*\.svg)["']/g, 'src="/static/img/$1"')
    .replaceAll(/src=["']\/assets\/([^"']*\.png)["']/g, 'src="/static/img/$1"')
    .replaceAll(/src=["']\/assets\/([^"']*\.jpg)["']/g, 'src="/static/img/$1"')
    .replaceAll(/src=["']\/assets\/([^"']*\.jpeg)["']/g, 'src="/static/img/$1"')
    .replaceAll(/src=["']\/assets\/([^"']*\.gif)["']/g, 'src="/static/img/$1"')
    .replaceAll(/src=["']\/assets\/([^"']*\.ico)["']/g, 'src="/static/img/$1"')

  mkdirSync(djangoTemplatesDir, { recursive: true })
  writeFileSync(djangoIndex, rewritten, 'utf-8')
  console.log('✅ index.html reescrito com novas URLs')
} catch (e) {
  console.warn('⚠️  Aviso: não foi possível reescrever index.html:', e.message)
}

// Ajusta referências nos arquivos CSS para apontar para os caminhos corretos
console.log('🔧 Ajustando referências CSS...')
const cssDir = resolve(djangoStatic, 'css')

if (existsSync(cssDir)) {
  const files = readdirSync(cssDir)
  const cssFiles = files.filter(file => file.endsWith('.css'))
  
  console.log(`📋 Arquivos CSS encontrados: ${cssFiles.join(', ')}`)
  
  for (const cssFile of cssFiles) {
    const cssPath = resolve(cssDir, cssFile)
    if (existsSync(cssPath)) {
      try {
        let css = readFileSync(cssPath, 'utf-8')
        
        // Ajusta referências para as novas pastas
        css = css.replaceAll(/url\(['"]?\.\.\/\.\.\/\.\.\/\.\.\/node_modules\/bootstrap-icons\/font\/fonts\//g, 'url("/static/css/')
        css = css.replaceAll(/url\(['"]?\.\.\/\.\.\/\.\.\/node_modules\/bootstrap-icons\/font\/fonts\//g, 'url("/static/css/')
        css = css.replaceAll(/url\(['"]?fonts\//g, 'url("/static/css/')
        css = css.replaceAll(/url\(['"]?\.\.\/assets\//g, 'url("/static/css/')
        css = css.replaceAll(/url\(['"]?assets\//g, 'url("/static/css/')
        css = css.replaceAll(/url\(['"]?\/assets\//g, 'url("/static/css/')
        css = css.replaceAll(/url\(['"]?bootstrap-icons\.woff2\?[^'"]*['"]?\)/g, 'url("/static/css/bootstrap-icons.woff2")')
        css = css.replaceAll(/url\(['"]?bootstrap-icons\.woff\?[^'"]*['"]?\)/g, 'url("/static/css/bootstrap-icons.woff")')
        
        // CORREÇÕES ESPECÍFICAS PARA IMAGENS SVG
        css = css.replaceAll(/url\(['"]?logo\.svg['"]?\)/g, 'url("/static/img/logo.svg")')
        css = css.replaceAll(/url\(['"]?logo-large\.svg['"]?\)/g, 'url("/static/img/logo-large.svg")')
        css = css.replaceAll(/url\(['"]?favicon\.svg['"]?\)/g, 'url("/static/img/favicon.svg")')
        css = css.replaceAll(/url\(['"]?favicon\.ico['"]?\)/g, 'url("/static/img/favicon.ico")')
        
        // CORREÇÕES GENÉRICAS PARA QUALQUER ARQUIVO SVG
        css = css.replaceAll(/url\(['"]?\/assets\/([^'"]*\.svg)['"]?\)/g, 'url("/static/img/$1")')
        css = css.replaceAll(/url\(['"]?assets\/([^'"]*\.svg)['"]?\)/g, 'url("/static/img/$1")')
        css = css.replaceAll(/url\(['"]?\.\.\/assets\/([^'"]*\.svg)['"]?\)/g, 'url("/static/img/$1")')
        
        writeFileSync(cssPath, css, 'utf-8')
        console.log(`✅ CSS ajustado: ${cssFile}`)
      } catch (e) {
        console.warn(`⚠️  Não foi possível ajustar CSS ${cssFile}:`, e.message)
      }
    }
  }
}

// Remove pastas desnecessárias
if (existsSync(resolve(djangoStatic, 'assets'))) {
  rmSync(resolve(djangoStatic, 'assets'), { recursive: true, force: true })
  console.log('🗑️  Pasta assets removida')
}

if (existsSync(resolve(djangoStatic, '.vite'))) {
  rmSync(resolve(djangoStatic, '.vite'), { recursive: true, force: true })
  console.log('🗑️  Pasta .vite removida')
}

if (existsSync(resolve(djangoStatic, 'static'))) {
  rmSync(resolve(djangoStatic, 'static'), { recursive: true, force: true })
  console.log('🗑️  Pasta static duplicada removida')
}

console.log('🚀 Build organizado em:', djangoStatic)
console.log('📁 Estrutura: js/, css/, img/')
console.log('🔍 Verifique se as imagens estão em:', resolve(djangoStatic, 'img'))


