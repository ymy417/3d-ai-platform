import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { projectApi } from '@/api/project'
import type {
  Project,
  ProjectListResponse,
  ProjectCreateRequest,
  ProjectUpdateRequest,
  ProjectFilterParams
} from '@/types/project'

export const useProjectStore = defineStore('projects', () => {
  // State
  const projects = ref<Project[]>([])
  const currentProject = ref<Project | null>(null)
  const loading = ref(false)
  const total = ref(0)
  const page = ref(1)
  const pageSize = ref(12)

  // Getters
  const hasProjects = computed(() => projects.value.length > 0)
  const isLoading = computed(() => loading.value)

  // Actions
  const fetchProjects = async (params?: ProjectFilterParams) => {
    loading.value = true
    try {
      const response = await projectApi.getProjects({
        page: page.value,
        page_size: pageSize.value,
        ...params
      })
      projects.value = response.data.items
      total.value = response.data.total
      return response.data
    } catch (error) {
      console.error('获取项目列表失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const createProject = async (data: ProjectCreateRequest) => {
    try {
      const response = await projectApi.createProject(data)
      projects.value.unshift(response.data)
      total.value++
      return response.data
    } catch (error) {
      console.error('创建项目失败:', error)
      throw error
    }
  }

  const getProjectDetail = async (id: number) => {
    loading.value = true
    try {
      const response = await projectApi.getProject(id)
      currentProject.value = response.data
      return response.data
    } catch (error) {
      console.error('获取项目详情失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const updateProject = async (id: number, data: ProjectUpdateRequest) => {
    try {
      const response = await projectApi.updateProject(id, data)
      // 更新列表中的项目
      const index = projects.value.findIndex(p => p.id === id)
      if (index !== -1) {
        projects.value[index] = response.data
      }
      // 更新当前项目
      if (currentProject.value?.id === id) {
        currentProject.value = response.data
      }
      return response.data
    } catch (error) {
      console.error('更新项目失败:', error)
      throw error
    }
  }

  const deleteProject = async (id: number) => {
    try {
      await projectApi.deleteProject(id)
      projects.value = projects.value.filter(p => p.id !== id)
      total.value--
      if (currentProject.value?.id === id) {
        currentProject.value = null
      }
    } catch (error) {
      console.error('删除项目失败:', error)
      throw error
    }
  }

  const duplicateProject = async (id: number) => {
    try {
      const response = await projectApi.duplicateProject(id)
      projects.value.unshift(response.data)
      total.value++
      return response.data
    } catch (error) {
      console.error('复制项目失败:', error)
      throw error
    }
  }



  const setPage = (newPage: number) => {
    page.value = newPage
  }

  const clearCurrentProject = () => {
    currentProject.value = null
  }

  return {
    // State
    projects,
    currentProject,
    loading,
    total,
    page,
    pageSize,
    // Getters
    hasProjects,
    isLoading,
    // Actions
    fetchProjects,
    createProject,
    getProjectDetail,
    updateProject,
    deleteProject,
    duplicateProject,
    setPage,
    clearCurrentProject
  }
})
