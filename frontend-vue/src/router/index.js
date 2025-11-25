import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '@/views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'
import DashboardView from '@/views/DashboardView.vue'
import UploadView from '@/views/UploadView.vue'
import ReportGenerationView from '@/views/ReportGenerationView.vue'
import ReportView from '@/views/ReportView.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: DashboardView,
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
    meta: { requiresGuest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: RegisterView,
    meta: { requiresGuest: true }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: DashboardView,
    meta: { requiresAuth: true }
  },
  {
    path: '/upload',
    name: 'Upload',
    component: UploadView,
    meta: { requiresAuth: true }
  },
  {
    path: '/generate-report',
    name: 'GenerateReport',
    component: ReportGenerationView,
    meta: { requiresAuth: true }
  },
  {
    path: '/report/:id',
    name: 'Report',
    component: ReportView,
    meta: { requiresAuth: true },
    props: true
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true'
  
  if (to.meta.requiresAuth && !isLoggedIn) {
    next('/login')
  } else if (to.meta.requiresGuest && isLoggedIn) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router