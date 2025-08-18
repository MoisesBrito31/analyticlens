<template>
  <div class="login-container">
    <div class="login-background">
      <BCard class="login-card shadow-lg border-0">
        <div class="text-center mb-4">
          <img src="@/assets/logo-large.svg" alt="analyticLens Logo" class="login-logo mb-3" />
          <h1 class="login-title">analyticLens</h1>
          <p class="login-subtitle">Sistema de Visão Computacional</p>
        </div>
        
        <BForm @submit.prevent="handleLogin" class="login-form">
          <BFormGroup label="Usuário" label-for="username" class="mb-3">
            <BInputGroup>
              <BInputGroupText>
                <i class="bi bi-person"></i>
              </BInputGroupText>
              <BFormInput
                id="username"
                v-model="username"
                type="text"
                placeholder="Digite seu usuário"
                required
                size="lg"
              />
            </BInputGroup>
          </BFormGroup>
          
          <BFormGroup label="Senha" label-for="password" class="mb-4">
            <BInputGroup>
              <BInputGroupText>
                <i class="bi bi-lock"></i>
              </BInputGroupText>
              <BFormInput
                id="password"
                v-model="password"
                type="password"
                placeholder="Digite sua senha"
                required
                size="lg"
              />
            </BInputGroup>
          </BFormGroup>
          
          <BButton
            type="submit"
            variant="primary"
            size="lg"
            class="w-100 login-btn"
            :disabled="loading"
          >
            <BSpinner v-if="loading" small class="me-2" />
            <i v-else class="bi bi-box-arrow-in-right me-2"></i>
            {{ loading ? 'Entrando...' : 'Entrar' }}
          </BButton>
        </BForm>
        
        <BAlert
          v-if="error"
          variant="danger"
          class="mt-3"
          show
        >
          <i class="bi bi-exclamation-triangle me-2"></i>
          {{ error }}
        </BAlert>
      </BCard>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  BCard,
  BForm,
  BFormGroup,
  BFormInput,
  BInputGroup,
  BInputGroupText,
  BButton,
  BAlert,
  BSpinner
} from 'bootstrap-vue-3'

const router = useRouter()
const auth = useAuthStore()

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function handleLogin() {
  if (!username.value || !password.value) {
    error.value = 'Por favor, preencha todos os campos'
    return
  }
  
  loading.value = true
  error.value = ''
  
  try {
    await auth.login({ username: username.value, password: password.value })
    router.push('/')
  } catch {
    error.value = 'Usuário ou senha incorretos'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-background {
  width: 100%;
  max-width: 450px;
  padding: 2rem;
}

.login-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 3rem 2rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.login-logo {
  width: 120px;
  height: 120px;
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.1));
}

.login-title {
  font-size: 2.5rem;
  font-weight: 700;
  background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 0.5rem;
}

.login-subtitle {
  color: #6b7280;
  font-size: 1.1rem;
  margin-bottom: 0;
}

.login-form {
  margin-top: 2rem;
}

.login-btn {
  background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
  border: none;
  padding: 0.875rem 1.5rem;
  font-size: 1.1rem;
  font-weight: 600;
  border-radius: 10px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
}

.login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4);
}

.login-btn:disabled {
  transform: none;
  box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
}

@media (max-width: 576px) {
  .login-background {
    padding: 1rem;
  }
  
  .login-card {
    padding: 2rem 1.5rem;
  }
  
  .login-title {
    font-size: 2rem;
  }
  
  .login-logo {
    width: 100px;
    height: 100px;
  }
}
</style>


