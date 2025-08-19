<template>
  <nav class="top-menu">
    <div class="menu-container">
      <!-- Logo/Nome da aplicação -->
      <div class="brand-section">
        <router-link to="/" class="brand-link">
          <div class="logo-container">
                         <img :src="getImagePath('logo.svg')" alt="analyticLens Logo" class="brand-logo">
          </div>
          <div class="brand-text">
            <span class="brand-name">analyticLens</span>
            <span class="brand-subtitle">Vision System</span>
          </div>
        </router-link>
      </div>

      <!-- Menu principal - Desktop -->
      <div class="nav-section desktop-nav">
        <router-link to="/" class="nav-item" active-class="active">
          <i class="bi bi-house-door"></i>
          <span>Início</span>
        </router-link>
        <router-link to="/machines" class="nav-item" active-class="active">
          <i class="bi bi-cpu"></i>
          <span>Máquinas</span>
        </router-link>
        <router-link to="/inspections" class="nav-item" active-class="active">
          <i class="bi bi-clipboard-check"></i>
          <span>Inspeções</span>
        </router-link>
        <router-link to="/configurations" class="nav-item" active-class="active">
          <i class="bi bi-gear"></i>
          <span>Configurações</span>
        </router-link>
      </div>

      <!-- Informações do usuário e ações -->
      <div class="user-section">
        <div class="user-info">
          <BAvatar 
            :text="getInitials(auth.username)" 
            variant="light"
            class="user-avatar"
            size="sm"
          />
          <div class="user-details">
            <span class="username">{{ auth.username || 'Usuário' }}</span>
            <span v-if="auth.role" class="user-role">{{ auth.role }}</span>
          </div>
        </div>
        
        <div class="user-actions">
          <button class="action-btn" @click="logout" title="Sair">
            <i class="bi bi-box-arrow-right"></i>
          </button>
        </div>
      </div>

      <!-- Botão hambúrguer para mobile -->
      <button class="hamburger-btn" @click="toggleMobileMenu" :class="{ 'active': showMobileMenu }">
        <span></span>
        <span></span>
        <span></span>
      </button>
    </div>

    <!-- Menu mobile -->
    <div class="mobile-menu" :class="{ 'show': showMobileMenu }">
      <div class="mobile-menu-header">
        <div class="mobile-user-info">
          <BAvatar 
            :text="getInitials(auth.username)" 
            variant="light"
            class="mobile-avatar"
            size="md"
          />
          <div class="mobile-user-details">
            <span class="mobile-username">{{ auth.username || 'Usuário' }}</span>
            <span v-if="auth.role" class="mobile-user-role">{{ auth.role }}</span>
          </div>
        </div>
        <button class="close-btn" @click="toggleMobileMenu">
          <i class="bi bi-x-lg"></i>
        </button>
      </div>
      
      <div class="mobile-nav">
        <router-link to="/" class="mobile-nav-item" @click="closeMobileMenu">
          <i class="bi bi-house-door"></i>
          <span>Início</span>
        </router-link>
        <router-link to="/machines" class="mobile-nav-item" @click="closeMobileMenu">
          <i class="bi bi-cpu"></i>
          <span>Máquinas</span>
        </router-link>
        <router-link to="/inspections" class="mobile-nav-item" @click="closeMobileMenu">
          <i class="bi bi-clipboard-check"></i>
          <span>Inspeções</span>
        </router-link>
        <router-link to="/configurations" class="mobile-nav-item" @click="closeMobileMenu">
          <i class="bi bi-gear"></i>
          <span>Configurações</span>
        </router-link>
      </div>
      
      <div class="mobile-actions">
        <button class="mobile-logout-btn" @click="handleMobileLogout">
          <i class="bi bi-box-arrow-right"></i>
          <span>Sair</span>
        </button>
      </div>
    </div>

    <!-- Overlay para fechar o menu mobile -->
    <div class="mobile-overlay" :class="{ 'show': showMobileMenu }" @click="closeMobileMenu"></div>
  </nav>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { BAvatar } from 'bootstrap-vue-3'

const auth = useAuthStore()
const router = useRouter()
const showMobileMenu = ref(false)

import { getImagePath } from '@/utils/imageRouter'

function getInitials(username) {
  if (!username) return 'U'
  return username
    .split(' ')
    .map(name => name.charAt(0))
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

function toggleMobileMenu() {
  showMobileMenu.value = !showMobileMenu.value
}

function closeMobileMenu() {
  showMobileMenu.value = false
}

async function handleMobileLogout() {
  closeMobileMenu()
  try {
    await auth.logout()
    router.push('/login')
  } catch (error) {
    console.error('Erro no logout:', error)
    router.push('/login')
  }
}

async function logout() {
  try {
    await auth.logout()
    router.push('/login')
  } catch (error) {
    console.error('Erro no logout:', error)
    router.push('/login')
  }
}
</script>

<style scoped>
.top-menu {
  background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.menu-container {
  width: 100%;
  margin: 0;
  padding: 0 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 70px;
  position: relative;
}

/* Brand Section */
.brand-section {
  flex-shrink: 0;
}

.brand-link {
  display: flex;
  align-items: center;
  text-decoration: none;
  color: inherit;
  transition: transform 0.2s ease;
}

.brand-link:hover {
  transform: translateY(-1px);
}

.logo-container {
  width: 40px;
  height: 40px;
  margin-right: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.brand-logo {
  width: 100%;
  height: 100%;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
}

.brand-text {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.brand-name {
  font-size: 1.5rem;
  font-weight: 700;
  color: #ffffff;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.brand-subtitle {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
  letter-spacing: 0.5px;
}

/* Navigation Section */
.nav-section {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  justify-content: center;
  margin: 0 2rem;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px 16px;
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  border-radius: 12px;
  transition: all 0.3s ease;
  min-width: 80px;
  position: relative;
}

.nav-item:hover {
  color: #ffffff;
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(-2px);
}

.nav-item.active {
  color: #ffffff;
  background: rgba(255, 255, 255, 0.15);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.nav-item i {
  font-size: 1.25rem;
  margin-bottom: 4px;
}

.nav-item span {
  font-size: 0.8rem;
  font-weight: 500;
  text-align: center;
}

/* User Section */
.user-section {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-shrink: 0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 25px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.user-info:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateY(-1px);
}

.user-avatar {
  flex-shrink: 0;
}

.user-details {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.username {
  font-size: 0.9rem;
  font-weight: 600;
  color: #ffffff;
}

.user-role {
  font-size: 0.7rem;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
}

.user-actions {
  display: flex;
  align-items: center;
}

.action-btn {
  width: 40px;
  height: 40px;
  border: none;
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.action-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.action-btn i {
  font-size: 1.1rem;
}

/* Hamburger Button */
.hamburger-btn {
  display: none;
  flex-direction: column;
  justify-content: space-around;
  width: 30px;
  height: 30px;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0;
  z-index: 1001;
}

.hamburger-btn span {
  width: 100%;
  height: 3px;
  background: #ffffff;
  border-radius: 2px;
  transition: all 0.3s ease;
  transform-origin: center;
}

.hamburger-btn.active span:nth-child(1) {
  transform: rotate(45deg) translate(6px, 6px);
}

.hamburger-btn.active span:nth-child(2) {
  opacity: 0;
}

.hamburger-btn.active span:nth-child(3) {
  transform: rotate(-45deg) translate(6px, -6px);
}

/* Mobile Menu */
.mobile-menu {
  position: fixed;
  top: 0;
  right: -300px;
  width: 300px;
  height: 100vh;
  background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
  box-shadow: -4px 0 20px rgba(0, 0, 0, 0.2);
  transition: right 0.3s ease;
  z-index: 1002;
  display: flex;
  flex-direction: column;
}

.mobile-menu.show {
  right: 0;
}

.mobile-menu-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 2rem 1.5rem 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.mobile-user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.mobile-avatar {
  flex-shrink: 0;
}

.mobile-user-details {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.mobile-username {
  font-size: 1rem;
  font-weight: 600;
  color: #ffffff;
}

.mobile-user-role {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
}

.close-btn {
  width: 40px;
  height: 40px;
  border: none;
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.close-btn i {
  font-size: 1.2rem;
}

.mobile-nav {
  flex: 1;
  padding: 1rem 0;
}

.mobile-nav-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 1rem 1.5rem;
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  transition: all 0.3s ease;
  border-left: 3px solid transparent;
}

.mobile-nav-item:hover {
  color: #ffffff;
  background: rgba(255, 255, 255, 0.1);
  border-left-color: rgba(255, 255, 255, 0.5);
}

.mobile-nav-item i {
  font-size: 1.25rem;
  width: 24px;
  text-align: center;
}

.mobile-nav-item span {
  font-size: 1rem;
  font-weight: 500;
}

.mobile-actions {
  padding: 1rem 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
}

.mobile-logout-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 12px;
  border: none;
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.mobile-logout-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.mobile-logout-btn i {
  font-size: 1.1rem;
}

.mobile-logout-btn span {
  font-size: 1rem;
  font-weight: 500;
}

/* Mobile Overlay */
.mobile-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s ease;
  z-index: 1001;
}

.mobile-overlay.show {
  opacity: 1;
  visibility: visible;
}

/* Responsividade */
@media (max-width: 1024px) {
  .menu-container {
    padding: 0 1rem;
  }
  
  .nav-section {
    margin: 0 1rem;
    gap: 4px;
  }
  
  .nav-item {
    min-width: 70px;
    padding: 10px 12px;
  }
  
  .nav-item span {
    font-size: 0.75rem;
  }
}

@media (max-width: 768px) {
  .menu-container {
    height: 60px;
    padding: 0 0.75rem;
  }
  
  .brand-name {
    font-size: 1.25rem;
  }
  
  .brand-subtitle {
    font-size: 0.7rem;
  }
  
  .nav-section {
    margin: 0 0.5rem;
    gap: 2px;
  }
  
  .nav-item {
    min-width: 60px;
    padding: 8px 10px;
  }
  
  .nav-item i {
    font-size: 1.1rem;
  }
  
  .nav-item span {
    font-size: 0.7rem;
  }
  
  .user-info {
    padding: 6px 12px;
  }
  
  .username {
    font-size: 0.8rem;
  }
  
  .user-role {
    font-size: 0.65rem;
  }
}

@media (max-width: 640px) {
  .menu-container {
    padding: 0 0.5rem;
    height: 55px;
  }
  
  .desktop-nav {
    display: none;
  }
  
  .hamburger-btn {
    display: flex;
  }
  
  .brand-subtitle {
    display: none;
  }
  
  .brand-name {
    display: none;
  }
  
  .user-section {
    display: none;
  }
  
  .logo-container {
    margin-right: 0;
    width: 35px;
    height: 35px;
  }
  
  .hamburger-btn {
    width: 28px;
    height: 28px;
  }
  
  .hamburger-btn span {
    height: 2.5px;
  }
}

@media (max-width: 480px) {
  .menu-container {
    padding: 0 0.25rem;
    height: 50px;
  }
  
  .logo-container {
    width: 30px;
    height: 30px;
  }
  
  .hamburger-btn {
    width: 25px;
    height: 25px;
  }
  
  .hamburger-btn span {
    height: 2px;
  }
}
</style>
