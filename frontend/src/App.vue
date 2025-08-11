<script setup>
// O header agora é gerenciado por cada view individual
</script>

<template>
  <div id="app">
    <router-view />
  </div>
</template>

<style>
#app {
  min-height: 100vh;
  background-color: #f8f9fa;
}

/* Layout responsivo para as regiões */
.app-container {
  min-height: 100vh;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.main-content {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 1rem;
  align-items: start;
  justify-content: center;
}

/* Para telas menores, empilhar verticalmente */
@media (max-width: 768px) {
  .main-content {
    grid-template-columns: 1fr;
  }
}

/* Para telas muito grandes, limitar largura máxima */
@media (min-width: 1400px) {
  .main-content {
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    max-width: 1400px;
    margin: 0 auto;
  }
}

/* Cards responsivos */
.card {
  height: fit-content;
  min-height: 200px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  border: none;
  border-radius: 8px;
}

.card-header {
  background-color: #fff;
  border-bottom: 1px solid #e9ecef;
  border-radius: 8px 8px 0 0 !important;
}

.card-body {
  padding: 1.25rem;
}

/* Ajustes para componentes específicos */
.inspection-info {
  grid-column: span 1;
}

.inspection-actions {
  grid-column: span 1;
}

.last-image {
  grid-column: span 1;
}

.live-stream {
  grid-column: span 2;
}

.tools-canvas {
  grid-column: span 2;
}

.tool-properties {
  grid-column: span 1;
}

/* Para telas menores, alguns componentes ocupam toda a largura */
@media (max-width: 768px) {
  .live-stream,
  .tools-canvas {
    grid-column: span 1;
  }
}

/* Estilos para o navbar */
.navbar-brand {
  font-weight: 600;
}

.nav-link {
  font-weight: 500;
}

.nav-link:hover {
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 0.375rem;
}

/* Estilos para botões de ação */
.btn-group .btn {
  border-radius: 0.375rem;
}

.btn-group .btn:not(:last-child) {
  margin-right: 0.25rem;
}
</style>
