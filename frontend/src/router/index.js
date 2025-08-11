import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import LiveView from '../views/LiveView.vue'
import InspectionsView from '../views/InspectionsView.vue'
import ImageLogView from '../views/ImageLogView.vue'
import ConfigurationsView from '../views/ConfigurationsView.vue'
import InspectionEditView from '../views/InspectionEditView.vue'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: LiveView, // Redireciona para ao vivo por padrão
      meta: { requiresAuth: true },
    },
    {
      path: '/live',
      name: 'live',
      component: LiveView,
      meta: { requiresAuth: true },
    },
    {
      path: '/inspections',
      name: 'inspections',
      component: InspectionsView,
      meta: { requiresAuth: true },
    },
    {
      path: '/image-log',
      name: 'image-log',
      component: ImageLogView,
      meta: { requiresAuth: true },
    },
    {
      path: '/configurations',
      name: 'configurations',
      component: ConfigurationsView,
      meta: { requiresAuth: true },
    },
    {
      path: '/inspection/edit',
      name: 'inspection-create',
      component: InspectionEditView,
      meta: { requiresAuth: true },
    },
    {
      path: '/inspection/edit/:id',
      name: 'inspection-edit',
      component: InspectionEditView,
      meta: { requiresAuth: true },
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/AboutView.vue'),
      meta: { requiresAuth: true },
    },
    { 
      path: '/login', 
      name: 'login', 
      component: LoginView 
    },
  ],
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  if (!auth.user) {
    await auth.loadMe()
  }
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }
})

export default router
