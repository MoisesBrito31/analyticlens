<template>
  <div>
    <TopMenu />
    <BContainer fluid class="mt-4">
      <BRow>
        <BCol cols="12">
          <BCard class="shadow-sm border-0">
            <BCardHeader class="bg-success text-white">
              <div class="d-flex align-items-center">
                <Icon name="clipboard-check" size="1.5rem" class="me-3" />
                <div>
                  <h2 class="mb-0">Sistema de Inspeções</h2>
                  <p class="mb-0 opacity-75">Gerencie e monitore suas inspeções de visão computacional</p>
                </div>
              </div>
            </BCardHeader>
            <BCardBody class="p-4 p-md-5">
              <BRow>
                <BCol cols="12">
                  <BAlert variant="success" show class="mb-4">
                    <Icon name="info-circle" size="1.2rem" class="me-2" />
                    <strong>Status:</strong> Sistema de inspeções em desenvolvimento.
                    Aqui você poderá visualizar, configurar e monitorar todas as inspeções do sistema.
                  </BAlert>
                  
                  <BCard class="border-0 bg-light">
                    <BCardBody class="text-center py-4 py-md-5">
                      <Icon name="clipboard-check" size="4rem" class="text-muted mb-3" style="opacity: 0.5;" />
                      <h5 class="text-muted">Funcionalidade em Desenvolvimento</h5>
                      <p class="text-muted mb-0">
                        A funcionalidade de gerenciamento de inspeções será implementada em breve.
                        Incluirá monitoramento em tempo real, histórico de resultados e configurações avançadas.
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
                      <Icon name="clock" size="1rem" class="me-1" />
                      Última verificação: {{ new Date().toLocaleString('pt-BR') }}
                    </small>
                    <BButton variant="outline-success" size="sm">
                      <Icon name="arrow-clockwise" size="1rem" class="me-1" />
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
import Icon from '@/components/Icon.vue'
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
  background: linear-gradient(135deg, #198754 0%, #20c997 100%) !important;
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
