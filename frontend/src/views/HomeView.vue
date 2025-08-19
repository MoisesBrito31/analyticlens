<script setup>
import TopMenu from '@/components/TopMenu.vue'
import { useAuthStore } from '@/stores/auth'

import {
  BContainer,
  BRow,
  BCol,
  BCard,
  BCardHeader,
  BCardBody,
  BListGroup,
  BListGroupItem,
  BBadge
} from 'bootstrap-vue-3'

const auth = useAuthStore()

import { getImagePath } from '@/utils/imageRouter'
</script>

<template>
  <div>
    <TopMenu />
    <BContainer fluid class="mt-4">
      <BRow>
        <BCol cols="12">
          <BCard class="shadow-sm border-0">
            <BCardHeader class="bg-primary text-white">
              <div class="d-flex align-items-center">
                <i class="bi bi-house me-3 fs-2"></i>
                <div>
                  <h2 class="mb-0">Bem-vindo ao analyticLens</h2>
                  <p class="mb-0 opacity-75">Sistema de Visão Computacional</p>
                </div>
              </div>
            </BCardHeader>
            <BCardBody class="p-4 p-md-5">
              <BRow class="g-4">
                <BCol cols="12" md="6">
                  <div class="text-center mb-4 mb-md-0">
                    <img :src="getImagePath('logo-large.svg')" alt="Logo" class="mb-3" style="width: 120px; height: 120px;" />
                    <h4 class="text-primary">Sistema Inteligente</h4>
                    <p class="text-muted">
                      Plataforma avançada para inspeção e análise de imagens usando 
                      inteligência artificial e visão computacional.
                    </p>
                  </div>
                </BCol>
                <BCol cols="12" md="6">
                  <BCard class="border-0 bg-light h-100">
                    <BCardBody class="p-3 p-md-4">
                      <h5 class="card-title">
                        <i class="bi bi-person-circle me-2"></i>
                        Informações do Usuário
                      </h5>
                      <BListGroup flush>
                        <BListGroupItem class="d-flex justify-content-between align-items-center">
                          <span>Usuário:</span>
                          <BBadge variant="primary">{{ auth.username || 'N/A' }}</BBadge>
                        </BListGroupItem>
                        <BListGroupItem class="d-flex justify-content-between align-items-center">
                          <span>Status:</span>
                          <BBadge variant="success">Conectado</BBadge>
                        </BListGroupItem>
                        <BListGroupItem v-if="auth.role" class="d-flex justify-content-between align-items-center">
                          <span>Função:</span>
                          <BBadge variant="info">{{ auth.role }}</BBadge>
                        </BListGroupItem>
                      </BListGroup>
                    </BCardBody>
                  </BCard>
                </BCol>
              </BRow>
              
              <BRow class="mt-4">
                <BCol cols="12">
                  <hr class="my-4">
                  <div class="text-center">
                    <p class="text-muted mb-0">
                      <i class="bi bi-clock me-1"></i>
                      Última atualização: {{ new Date().toLocaleString('pt-BR') }}
                    </p>
                  </div>
                </BCol>
              </BRow>
            </BCardBody>
          </BCard>
        </BCol>
      </BRow>
    </BContainer>
  </div>
</template>

<style scoped>
.card-header {
  background: linear-gradient(135deg, #0d6efd 0%, #0a58ca 100%) !important;
}

.opacity-75 {
  opacity: 0.75;
}

.fs-2 {
  font-size: 1.5rem !important;
}

/* Responsividade para telas menores */
@media (max-width: 768px) {
  .container-fluid {
    padding-left: 0.5rem !important;
    padding-right: 0.5rem !important;
  }
  
  .card-body {
    padding: 1rem !important;
  }
  
  .card-header {
    padding: 1rem !important;
  }
  
  .card-header h2 {
    font-size: 1.5rem !important;
  }
  
  .card-header p {
    font-size: 0.9rem !important;
  }
  
  .fs-2 {
    font-size: 1.25rem !important;
  }
}

@media (max-width: 576px) {
  .container-fluid {
    padding-left: 0.25rem !important;
    padding-right: 0.25rem !important;
  }
  
  .mt-4 {
    margin-top: 0.5rem !important;
  }
  
  .card-body {
    padding: 0.75rem !important;
  }
  
  .card-header {
    padding: 0.75rem !important;
  }
  
  .card-header h2 {
    font-size: 1.25rem !important;
  }
  
  .card-header p {
    font-size: 0.8rem !important;
  }
  
  .fs-2 {
    font-size: 1.1rem !important;
  }
  
  .g-4 {
    --bs-gutter-x: 0.5rem !important;
    --bs-gutter-y: 0.5rem !important;
  }
}
</style>
