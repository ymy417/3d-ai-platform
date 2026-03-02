import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import HomeView from '../views/HomeView.vue'
import CreateView from '../views/CreateView.vue'
import ModelingView from '../views/ModelingView.vue'
import TemplatesView from '../views/TemplatesView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import ProfileView from '../views/ProfileView.vue'
import ProfileSetupView from '../views/ProfileSetupView.vue'
import LibraryView from '../views/LibraryView.vue'
import ProjectDetailView from '../views/ProjectDetailView.vue'
import GalleryView from '../views/GalleryView.vue'
import GalleryProjectDetailView from '../views/GalleryProjectDetailView.vue'
import UserDetailView from '../views/UserDetailView.vue'
import NotFound from '../views/NotFound.vue'

// Admin
import AdminLayout from '../layouts/AdminLayout.vue'
import AdminDashboard from '../views/admin/DashboardView.vue'
import AdminUsers from '../views/admin/UsersView.vue'
import AdminAppeals from '../views/admin/AppealsView.vue'
import AdminProjects from '../views/admin/ProjectsView.vue'
import AdminReports from '../views/admin/ReportsView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/create',
      name: 'create',
      component: CreateView,
      meta: { requiresAuth: true },
    },
    {
      path: '/modeling',
      name: 'modeling',
      component: ModelingView,
      meta: { requiresAuth: true },
    },
    {
      path: '/templates',
      name: 'templates',
      component: TemplatesView,
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { guest: true },
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
      meta: { guest: true },
    },
    {
      path: '/profile',
      name: 'profile',
      component: ProfileView,
      meta: { requiresAuth: true },
    },
    {
      path: '/profile-setup',
      name: 'profile-setup',
      component: ProfileSetupView,
      meta: { requiresAuth: true },
    },
    {
      path: '/library',
      name: 'library',
      component: LibraryView,
      meta: { requiresAuth: true },
    },
    {
      path: '/library/project/:id',
      name: 'project-detail',
      component: ProjectDetailView,
      meta: { requiresAuth: true },
    },
    {
      path: '/gallery',
      name: 'gallery',
      component: GalleryView,
    },
    {
      path: '/gallery/project/:id',
      name: 'gallery-project-detail',
      component: GalleryProjectDetailView,
    },
    {
      path: '/gallery/user/:id',
      name: 'gallery-user-detail',
      component: UserDetailView,
    },
    // Admin routes
    {
      path: '/admin',
      component: AdminLayout,
      meta: { requiresAuth: true, requiresAdmin: true },
      children: [
        {
          path: '',
          redirect: '/admin/dashboard',
        },
        {
          path: 'dashboard',
          name: 'admin-dashboard',
          component: AdminDashboard,
        },
        {
          path: 'users',
          name: 'admin-users',
          component: AdminUsers,
        },
        {
          path: 'appeals',
          name: 'admin-appeals',
          component: AdminAppeals,
        },
        {
          path: 'projects',
          name: 'admin-projects',
          component: AdminProjects,
        },
        {
          path: 'reports',
          name: 'admin-reports',
          component: AdminReports,
        },
      ],
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: NotFound,
    },
  ],
})

router.beforeEach(async (to, from, next) => {
  const token = localStorage.getItem('token')
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !token) {
    next({ name: 'login', query: { redirect: to.fullPath } })
    return
  }
  
  if (to.meta.requiresAdmin) {
    if (!token) {
      next({ name: 'login', query: { redirect: to.fullPath } })
      return
    }
    
    // 如果有 token 但没有用户信息，先获取用户信息
    if (!authStore.user) {
      await authStore.fetchUser()
    }
    
    if (!authStore.isAdmin) {
      next({ name: 'home' })
      return
    }
  }
  
  if (to.meta.guest && token) {
    next({ name: 'home' })
    return
  }
  
  next()
})

export default router
