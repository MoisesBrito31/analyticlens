import { defineStore } from 'pinia'
import { apiFetch } from '@/utils/http'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    loading: false,
  }),
  getters: {
    isAuthenticated: (s) => !!s.user,
    roles: (s) => s.user?.roles ?? [],
  },
  actions: {
    async getCsrf() {
      await apiFetch('/api/auth/csrf', { method: 'GET' })
    },
    async loadMe() {
      try {
        const r = await apiFetch('/api/auth/me', { method: 'GET' })
        this.user = await r.json()
      } catch {
        this.user = null
      }
    },
    async login(payload) {
      this.loading = true
      try {
        await this.getCsrf()
        const r = await apiFetch('/api/auth/login', {
          method: 'POST',
          body: JSON.stringify(payload),
        })
        if (!r.ok) throw new Error('Login inválido')
        await this.loadMe()
      } finally {
        this.loading = false
      }
    },
    async logout() {
      await apiFetch('/api/auth/logout', { method: 'POST' })
      this.user = null
    },
  },
})


