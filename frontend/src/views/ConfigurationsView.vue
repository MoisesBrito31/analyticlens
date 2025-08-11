<template>
  <div class="app-container">
    <AppHeader />
    
    <div class="main-content">
      <!-- Configurações Gerais -->
      <div class="card">
        <div class="card-header">
          <h6 class="mb-0">
            <i class="bi bi-gear text-primary me-2"></i>
            Configurações Gerais
          </h6>
        </div>
        <div class="card-body">
          <div class="text-center py-5">
            <i class="bi bi-gear text-muted" style="font-size: 3rem;"></i>
            <p class="text-muted mt-3">Configurações serão implementadas aqui</p>
            <p class="text-muted small">Parâmetros globais da aplicação</p>
          </div>
        </div>
      </div>
      
      <!-- Configurações de Câmera -->
      <div class="card">
        <div class="card-header">
          <h6 class="mb-0">
            <i class="bi bi-camera text-info me-2"></i>
            Configurações de Câmera
          </h6>
        </div>
        <div class="card-body">
          <div class="text-center py-5">
            <i class="bi bi-camera text-muted" style="font-size: 3rem;"></i>
            <p class="text-muted mt-3">Configurações de câmera</p>
            <p class="text-muted small">IP, RTSP, resolução, FPS</p>
          </div>
        </div>
      </div>
      
      <!-- Configurações de Rede -->
      <div class="card">
        <div class="card-header">
          <h6 class="mb-0">
            <i class="bi bi-wifi text-success me-2"></i>
            Configurações de Rede
          </h6>
        </div>
        <div class="card-body">
          <div class="text-center py-5">
            <i class="bi bi-wifi text-muted" style="font-size: 3rem;"></i>
            <p class="text-muted mt-3">Configurações de rede</p>
            <p class="text-muted small">Portas, IPs, firewall</p>
          </div>
        </div>
      </div>
      
      <!-- Configurações de Banco -->
      <div class="card">
        <div class="card-header">
          <h6 class="mb-0">
            <i class="bi bi-database text-warning me-2"></i>
            Configurações de Banco
          </h6>
        </div>
        <div class="card-body">
          <div class="text-center py-5">
            <i class="bi bi-database text-muted" style="font-size: 3rem;"></i>
            <p class="text-muted mt-3">Configurações de banco</p>
            <p class="text-muted small">Backup, limpeza, retenção</p>
          </div>
        </div>
      </div>
      
      <!-- Configurações de Log -->
      <div class="card">
        <div class="card-header">
          <h6 class="mb-0">
            <i class="bi bi-journal-text text-danger me-2"></i>
            Configurações de Log
          </h6>
        </div>
        <div class="card-body">
          <div class="text-center py-5">
            <i class="bi bi-journal-text text-muted" style="font-size: 3rem;"></i>
            <p class="text-muted mt-3">Configurações de log</p>
            <p class="text-muted small">Nível, rotação, retenção</p>
          </div>
        </div>
      </div>
      
      <!-- Configurações de Segurança -->
      <div class="card">
        <div class="card-header">
          <h6 class="mb-0">
            <i class="bi bi-shield-lock text-dark me-2"></i>
            Configurações de Segurança
          </h6>
        </div>
        <div class="card-body">
          <div class="text-center py-5">
            <i class="bi bi-shield-lock text-muted" style="font-size: 3rem;"></i>
            <p class="text-muted mt-3">Configurações de segurança</p>
            <p class="text-muted small">Usuários, permissões, SSL</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import AppHeader from '@/components/AppHeader.vue'
</script>
