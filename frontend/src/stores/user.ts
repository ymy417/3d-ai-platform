import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { userApi } from '@/api/user'
import type {
  User,
  UserPublicResponse
} from '@/types/user'

export const useUserStore = defineStore('user', () => {
  // State
  const currentUser = ref<User | null>(null)
  const userProjects = ref<any[]>([])
  const loading = ref(false)

  // Getters
  const isLoading = computed(() => loading.value)
  const hasUser = computed(() => currentUser.value !== null)

  // Actions
  const fetchPublicUserInfo = async (userId: number) => {
    loading.value = true
    try {
      const response = await userApi.getPublicUserInfo(userId)
      currentUser.value = response.data.user
      userProjects.value = response.data.projects
      return response.data
    } catch (error) {
      console.error('获取用户信息失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const clearCurrentUser = () => {
    currentUser.value = null
    userProjects.value = []
  }

  return {
    // State
    currentUser,
    userProjects,
    loading,
    // Getters
    isLoading,
    hasUser,
    // Actions
    fetchPublicUserInfo,
    clearCurrentUser
  }
})
