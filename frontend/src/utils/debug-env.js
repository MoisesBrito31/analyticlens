/**
 * Script de debug para verificar variáveis de ambiente
 * Use no console do navegador para diagnosticar problemas
 */

export function debugEnvironment() {
  console.log('🔍 DEBUG: Variáveis de Ambiente');
  console.log('================================');
  
  // Variáveis do Vite
  console.log('import.meta.env.DEV:', import.meta.env?.DEV);
  console.log('import.meta.env.MODE:', import.meta.env?.MODE);
  console.log('import.meta.env.PROD:', import.meta.env?.PROD);
  console.log('import.meta.env.SSR:', import.meta.env?.SSR);
  
  // Informações do navegador
  console.log('window.location.hostname:', window.location.hostname);
  console.log('window.location.port:', window.location.port);
  console.log('window.location.protocol:', window.location.protocol);
  console.log('window.location.href:', window.location.href);
  
  // Verificações específicas
  console.log('É localhost?', window.location.hostname === 'localhost');
  console.log('É 127.0.0.1?', window.location.hostname === '127.0.0.1');
  console.log('Porta é 5173?', window.location.port === '5173');
  console.log('Protocolo é HTTP?', window.location.protocol === 'http:');
  
  // Resultado da detecção
  const isDev = import.meta.env?.DEV === true;
  const isProd = import.meta.env?.MODE === 'production';
  
  console.log('🔧 RESULTADO:');
  console.log('É desenvolvimento (Vite)?', isDev);
  console.log('É produção (Vite)?', isProd);
  console.log('Modo detectado:', isDev ? 'DEVELOPMENT' : isProd ? 'PRODUCTION' : 'UNKNOWN');
  
  return {
    isDev,
    isProd,
    mode: import.meta.env?.MODE,
    hostname: window.location.hostname,
    port: window.location.port
  };
}

// Função para testar o imageRouter
export function testImageRouter() {
  const { getImagePath } = require('./imageRouter.js');
  
  console.log('🧪 TESTE: Image Router');
  console.log('========================');
  
  const testImages = ['logo.svg', 'logo-large.svg', 'favicon.ico'];
  
  testImages.forEach(img => {
    const path = getImagePath(img);
    console.log(`${img}: ${path}`);
  });
}

// Auto-executa se estiver no console
if (typeof console !== 'undefined') {
  console.log('🚀 Debug Environment carregado!');
  console.log('Use debugEnvironment() para ver as variáveis');
  console.log('Use testImageRouter() para testar o router');
}
