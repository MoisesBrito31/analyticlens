/**
 * Utilitário para montar URL de mídia (MEDIA_URL) conforme ambiente.
 * Recebe um caminho relativo (ex.: 'inspections/1/ref.jpg') e retorna a URL completa.
 */

function isDevelopment() {
  if (import.meta.env?.DEV === true) return true;
  if (import.meta.env?.MODE === 'production') return false;
  const isLocalDev = (
    window.location.hostname === 'localhost' ||
    window.location.hostname === '127.0.0.1' ||
    window.location.port === '5173' ||
    window.location.protocol === 'http:'
  );
  if (isLocalDev && !import.meta.env?.DEV) return false;
  return isLocalDev;
}

/**
 * Monta URL de mídia correta conforme o ambiente atual.
 * - Dev (Vite): o backend Django geralmente roda em 8000.
 * - Build/Produção (servido pelo Django): usa caminho relativo a partir da raiz.
 * @param {string} mediaPath Caminho relativo salvo no banco (ex.: 'inspections/2/foto.jpg')
 * @param {object} opts Config opcional: { djangoPort?: number, djangoHost?: string }
 * @returns {string} URL absoluta para a mídia
 */
export function getMediaUrl(mediaPath, opts = {}) {
  if (!mediaPath) return '';
  const isDev = isDevelopment();
  const cleanPath = String(mediaPath).replace(/^\/+/, ''); // remove leading slashes
  const base = 'media/' + cleanPath;

  if (isDev) {
    const host = opts.djangoHost || window.location.hostname || 'localhost';
    const port = String(opts.djangoPort || 8000);
    const protocol = window.location.protocol === 'https:' ? 'https:' : 'http:';
    return `${protocol}//${host}:${port}/${base}`;
  }
  // Produção: o Django serve /media/ no mesmo domínio
  return `/${base}`;
}

export default getMediaUrl;


