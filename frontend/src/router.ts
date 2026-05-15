import { createRouter, createWebHistory, type RouteLocationNormalizedLoaded } from 'vue-router'
import DatasetsView from './views/DatasetsView.vue'
import DatasetDetailView from './views/DatasetDetailView.vue'
import LogsView from './views/LogsView.vue'
import LoginView from './views/LoginView.vue'
import UpdatePasswordView from './views/UpdatePasswordView.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
    meta: { requiresAuth: false }
  },
  {
    path: '/update-password',
    name: 'UpdatePassword',
    component: UpdatePasswordView,
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    name: 'Datasets',
    component: DatasetsView,
    meta: { requiresAuth: true }
  },
  {
    path: '/dataset/:id',
    name: 'DatasetDetail',
    component: DatasetDetailView,
    props: (route: RouteLocationNormalizedLoaded) => ({ sourceId: Number(route.params.id) }),
    meta: { requiresAuth: true }
  },
  {
    path: '/logs',
    name: 'Logs',
    component: LogsView,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Auth guard
router.beforeEach((to, _from, next) => {
  const token = sessionStorage.getItem('auth_token')
  const hasToken = !!token
  const requiresAuth = to.meta.requiresAuth !== false

  if (!hasToken) {
    sessionStorage.removeItem('auth_token')
  }

  if (requiresAuth && !hasToken) {
    next('/login')
  } else if (to.path === '/login' && hasToken) {
    next('/')
  } else {
    next()
  }
})

export default router