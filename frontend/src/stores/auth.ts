import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/types/user'
import { authApi } from '@/api/auth'
import router from '@/router'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))
  const loading = ref(false)
  const error = ref<string | null>(null)

  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const isCreator = computed(() => user.value?.role === 'creator' || user.value?.role === 'admin')

  async function login(email: string, password: string) {
    try {
      loading.value = true
      error.value = null
      
      const response = await authApi.login({ email, password })
      
      token.value = response.access_token
      user.value = response.user
      
      localStorage.setItem('token', response.access_token)
      
      return true
    } catch (err: any) {
      error.value = err.response?.data?.detail || '登录失败，请检查邮箱和密码'
      return false
    } finally {
      loading.value = false
    }
  }

  async function register(username: string, email: string, password: string) {
    try {
      loading.value = true
      error.value = null
      
      await authApi.register({ username, email, password })
      
      return await login(email, password)
    } catch (err: any) {
      error.value = err.response?.data?.detail || '注册失败，请稍后重试'
      return false
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    try {
      await authApi.logout()
    } catch (err) {
      console.error('Logout error:', err)
    } finally {
      token.value = null
      user.value = null
      localStorage.removeItem('token')
      router.push('/login')
    }
  }

  async function fetchUser() {
    if (!token.value) return false
    
    try {
      loading.value = true
      const response = await authApi.getCurrentUser()
      user.value = response
      return true
    } catch (err) {
      token.value = null
      user.value = null
      localStorage.removeItem('token')
      return false
    } finally {
      loading.value = false
    }
  }

  async function updateProfile(data: Partial<User>) {
    try {
      loading.value = true
      error.value = null
      
      const response = await authApi.updateProfile(data)
      user.value = response
      
      return true
    } catch (err: any) {
      error.value = err.response?.data?.detail || '更新失败'
      return false
    } finally {
      loading.value = false
    }
  }

  async function changePassword(oldPassword: string, newPassword: string) {
    try {
      loading.value = true
      error.value = null
      
      await authApi.changePassword({ old_password: oldPassword, new_password: newPassword })
      
      return true
    } catch (err: any) {
      error.value = err.response?.data?.detail || '密码修改失败'
      return false
    } finally {
      loading.value = false
    }
  }

  function clearError() {
    error.value = null
  }

  return {
    user,
    token,
    loading,
    error,
    isAuthenticated,
    isAdmin,
    isCreator,
    login,
    register,
    logout,
    fetchUser,
    updateProfile,
    changePassword,
    clearError,
  }
})
