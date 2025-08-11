<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
    <div class="container-fluid">
      <!-- Logo/Nome da aplicação -->
      <router-link class="navbar-brand" to="/">
        analyticLens
      </router-link>

      <!-- Menu principal -->
      <div class="navbar-nav me-auto">
        <router-link class="nav-link" to="/live">
          <i class="bi bi-camera-video"></i> Ao Vivo
        </router-link>
        <router-link class="nav-link" to="/inspections">
          <i class="bi bi-clipboard-check"></i> Inspeções
        </router-link>
        <router-link class="nav-link" to="/image-log">
          <i class="bi bi-images"></i> Log de Imagens
        </router-link>
        <router-link class="nav-link" to="/configurations">
          <i class="bi bi-gear"></i> Configurações
        </router-link>
      </div>

      <!-- Informações do usuário e ações -->
      <div class="navbar-nav ms-auto">
        <div class="nav-item dropdown">
          <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
            <i class="bi bi-person-circle"></i> {{ auth.user?.username }}
          </a>
          <ul class="dropdown-menu dropdown-menu-end">
            <li><a class="dropdown-item" href="#" @click="logout">Logout</a></li>
          </ul>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()

async function logout() {
  await auth.logout()
  router.push('/login')
}
</script>
