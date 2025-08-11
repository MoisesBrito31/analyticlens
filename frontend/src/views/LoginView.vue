<template>
  <div class="container py-5" style="max-width: 420px;">
    <h1 class="h4 mb-4">Entrar</h1>
    <form @submit.prevent="onSubmit">
      <div class="mb-3">
        <label class="form-label">Usuário</label>
        <input v-model="username" class="form-control" autocomplete="username" />
      </div>
      <div class="mb-3">
        <label class="form-label">Senha</label>
        <input v-model="password" type="password" class="form-control" autocomplete="current-password" />
      </div>
      <button class="btn btn-primary w-100" :disabled="auth.loading">Entrar</button>
    </form>
    <p v-if="error" class="text-danger mt-3">{{ error }}</p>
  </div>
  
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const username = ref('')
const password = ref('')
const error = ref('')

async function onSubmit() {
  error.value = ''
  try {
    await auth.login({ username: username.value, password: password.value })
    const redirect = route.query.redirect || '/'
    router.replace(redirect)
  } catch (e) {
    error.value = 'Usuário ou senha inválidos'
  }
}
</script>


