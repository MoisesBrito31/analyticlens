/**
 * Utilitário para roteamento inteligente de imagens
 * Detecta automaticamente se estamos em desenvolvimento ou produção
 * e retorna o caminho correto para as imagens
 */

/**
 * Detecta se estamos em desenvolvimento ou produção
 * @returns {boolean} true se estiver em desenvolvimento
 */
function isDevelopment() {
  // Prioriza as variáveis de ambiente do Vite (mais confiáveis)
  if (import.meta.env?.DEV === true) {
    return true;
  }
  
  if (import.meta.env?.MODE === 'production') {
    return false;
  }
  
  // Se não temos as variáveis do Vite, usa fallback baseado no contexto
  // Verifica se estamos rodando localmente (desenvolvimento)
  const isLocalDev = (
    window.location.hostname === 'localhost' ||
    window.location.hostname === '127.0.0.1' ||
    window.location.port === '5173' ||  // Vite padrão
    window.location.port === '3000' ||  // Outras portas comuns
    window.location.protocol === 'http:'  // HTTP local
  );
  
  // Se estamos em localhost mas não temos as variáveis do Vite,
  // provavelmente é um build local sendo testado
  if (isLocalDev && !import.meta.env?.DEV) {
    return false; // Assume produção
  }
  
  return isLocalDev;
}

/**
 * Obtém o caminho correto para uma imagem baseado no ambiente
 * @param {string} imageName - Nome do arquivo de imagem (ex: 'logo.svg', 'logo-large.svg')
 * @returns {string} Caminho completo para a imagem
 */
export function getImagePath(imageName) {
  const isDev = isDevelopment();
  
  if (isDev) {
    // Em desenvolvimento: usa caminho que o Vite resolve
    // O Vite resolve automaticamente assets da pasta src/assets/
    // Precisa ser caminho absoluto para funcionar em rotas aninhadas (ex.: /machines/123)
    return `/src/assets/${imageName}`;
  } else {
    // Em produção: usa /static/img/ do Django
    return `/static/img/${imageName}`;
  }
}

// Exporta a função como default para uso mais simples
export default getImagePath;
