<template>
  <div>
    <TopMenu />
    <BContainer fluid class="mt-4">
      <BRow>
        <BCol cols="12">
          <BCard class="shadow-sm border-0">
            <BCardHeader class="bg-info text-white">
              <div class="d-flex align-items-center">
                <i class="bi bi-cpu me-3 fs-2"></i>
                <div>
                  <h2 class="mb-0">Lista de Máquinas de Visão (VM)</h2>
                  <p class="mb-0 opacity-75">Gerencie suas máquinas de visão conectadas</p>
                </div>
              </div>
            </BCardHeader>
            <BCardBody class="p-4 p-md-5">
              <BRow>
                <BCol cols="12">
                  <BAlert variant="info" show class="mb-4">
                    <i class="bi bi-info-circle me-2"></i>
                    <strong>Status:</strong> Sistema de máquinas de visão em desenvolvimento.
                    Aqui você poderá visualizar e gerenciar todas as máquinas conectadas ao sistema.
                  </BAlert>
                  
                  <BCard class="border-0 bg-light">
                    <BCardBody class="text-center py-4 py-md-5">
                      <i class="bi bi-cpu text-muted mb-3" style="font-size: 4rem; opacity: 0.5;"></i>
                      <h5 class="text-muted">Funcionalidade em Desenvolvimento</h5>
                      <p class="text-muted mb-0">
                        A funcionalidade de listagem e gerenciamento de máquinas de visão 
                        será implementada em breve.
                      </p>
                    </BCardBody>
                  </BCard>
                </BCol>
              </BRow>
              
              <BRow class="mt-4">
                <BCol cols="12">
                  <hr class="my-4">
                  <div class="d-flex justify-content-between align-items-center">
                    <small class="text-muted">
                      <i class="bi bi-clock me-1"></i>
                      Última verificação: {{ new Date().toLocaleString('pt-BR') }}
                    </small>
                    <BButton variant="outline-primary" size="sm">
                      <i class="bi bi-arrow-clockwise me-1"></i>
                      Atualizar
                    </BButton>
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

<script setup>
import TopMenu from '@/components/TopMenu.vue'
import {
  BContainer,
  BRow,
  BCol,
  BCard,
  BCardHeader,
  BCardBody,
  BAlert,
  BButton
} from 'bootstrap-vue-3'
</script>

<style scoped>
.card-header {
  background: linear-gradient(135deg, #0dcaf0 0%, #0aa2c0 100%) !important;
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
  
  .py-4.py-md-5 {
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
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
  
  .py-4.py-md-5 {
    padding-top: 1.5rem !important;
    padding-bottom: 1.5rem !important;
  }
  
  .d-flex.justify-content-between {
    flex-direction: column !important;
    gap: 0.5rem !important;
    align-items: stretch !important;
  }
  
  .d-flex.justify-content-between .btn {
    width: 100% !important;
  }
}
</style>
