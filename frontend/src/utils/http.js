export async function apiFetch(input, init = {}) {
  const headers = new Headers(init.headers)
  if (init.method && init.method !== 'GET' && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }
  // Adiciona CSRF automaticamente quando necessário
  const isWrite = init.method && init.method !== 'GET'
  if (isWrite && !headers.has('X-CSRFToken')) {
    const csrftoken = document.cookie.split('; ').find(c => c.startsWith('csrftoken='))?.split('=')[1]
    if (csrftoken) headers.set('X-CSRFToken', csrftoken)
  }
  const res = await fetch(input, { credentials: 'include', ...init, headers })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res
}


