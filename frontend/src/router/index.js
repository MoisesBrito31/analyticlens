import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import HomeView from '@/views/HomeView.vue'
import LoginView from '@/views/LoginView.vue'
import MachinesView from '@/views/MachinesView.vue'
import InspectionsView from '@/views/InspectionsView.vue'
import ConfigurationsView from '@/views/ConfigurationsView.vue'
import NotFoundView from '@/views/NotFoundView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: { requiresAuth: true }
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/machines',
      name: 'machines',
      component: MachinesView,
      meta: { requiresAuth: true }
    },
    {
      path: '/machines/new',
      name: 'machines-new',
      component: MachinesView, // Por enquanto usa o mesmo componente
      meta: { requiresAuth: true }
    },
    {
      path: '/machines/:id',
      name: 'machines-detail',
      component: MachinesView, // Por enquanto usa o mesmo componente
      meta: { requiresAuth: true }
    },
    {
      path: '/inspections',
      name: 'inspections',
      component: InspectionsView,
      meta: { requiresAuth: true }
    },
    {
      path: '/configurations',
      name: 'configurations',
      component: ConfigurationsView,
      meta: { requiresAuth: true }
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: NotFoundView,
      beforeEnter: (to, from, next) => {
        // Excluir rotas que devem ser tratadas pelo Django
        const djangoRoutes = ['/admin', '/api', '/static', '/media']
        const isDjangoRoute = djangoRoutes.some(route => to.path.startsWith(route))
        
        if (isDjangoRoute) {
          // Se for uma rota do Django, não processar no Vue
          console.log(`🚫 Rota do Django interceptada: ${to.path}`)
          next(false)
        } else {
          // Se não for rota do Django, mostrar página 404
          console.log(`🎭 Página 404 para: ${to.path}`)
          next()
        }
      }
    }
  ]
})

router.beforeEach((to, from, next) => {
  const auth = useAuthStore()
  
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    next('/login')
  } else {
    next()
  }
})

export default router
