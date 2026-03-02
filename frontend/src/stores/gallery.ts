import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { projectApi } from '@/api/project'
import type {
  Project,
  ProjectListResponse,
  ProjectFilterParams,
  Comment,
  CommentCreateRequest,
  LikeResponse,
  FavoriteResponse,
  DownloadResponse
} from '@/types/project'

export const useGalleryStore = defineStore('gallery', () => {
  // State
  const projects = ref<Project[]>([])
  const currentProject = ref<Project | null>(null)
  const comments = ref<Comment[]>([])
  const loading = ref(false)
  const total = ref(0)
  const page = ref(1)
  const pageSize = ref(12)

  // Getters
  const hasProjects = computed(() => projects.value.length > 0)
  const isLoading = computed(() => loading.value)

  // Actions
  const fetchPublicProjects = async (params?: ProjectFilterParams) => {
    loading.value = true
    try {
      const response = await projectApi.getPublicProjects({
        page: page.value,
        page_size: pageSize.value,
        ...params
      })
      projects.value = response.data.items
      total.value = response.data.total
      return response.data
    } catch (error) {
      console.error('获取公共项目列表失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const fetchPublicProject = async (id: string) => {
    loading.value = true
    try {
      const response = await projectApi.getPublicProject(Number(id))
      currentProject.value = response.data
      return response.data
    } catch (error) {
      console.error('获取公共项目详情失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const toggleLike = async (id: string) => {
    try {
      const response = await projectApi.toggleLike(Number(id))
      return response.data
    } catch (error) {
      console.error('点赞操作失败:', error)
      throw error
    }
  }

  const toggleFavorite = async (id: string) => {
    try {
      const response = await projectApi.toggleFavorite(Number(id))
      return response.data
    } catch (error) {
      console.error('收藏操作失败:', error)
      throw error
    }
  }

  const fetchProjectComments = async (id: string) => {
    try {
      const response = await projectApi.getProjectComments(Number(id))
      comments.value = response.data
      return response.data
    } catch (error) {
      console.error('获取评论失败:', error)
      throw error
    }
  }

  const addComment = async (id: string, data: CommentCreateRequest) => {
    try {
      const response = await projectApi.addComment(Number(id), data)
      comments.value.unshift(response.data)
      return response.data
    } catch (error) {
      console.error('添加评论失败:', error)
      throw error
    }
  }

  const downloadProject = async (id: string) => {
    try {
      const response = await projectApi.downloadProject(Number(id))
      return response.data
    } catch (error) {
      console.error('下载项目失败:', error)
      throw error
    }
  }

  const publishProject = async (id: number, isPublic: boolean, allowDownload?: boolean) => {
    try {
      const response = await projectApi.publishProject(id, isPublic, allowDownload)
      // 更新列表中的项目
      const index = projects.value.findIndex(p => p.id === id)
      if (index !== -1) {
        projects.value[index].is_public = response.data.is_public
        projects.value[index].allow_download = response.data.allow_download
        if (response.data.status) {
          projects.value[index].status = response.data.status
        }
      }
      // 更新当前项目
      if (currentProject.value?.id === id) {
        currentProject.value.is_public = response.data.is_public
        currentProject.value.allow_download = response.data.allow_download
        if (response.data.status) {
          currentProject.value.status = response.data.status
        }
      }
      return response.data
    } catch (error) {
      console.error('发布项目失败:', error)
      throw error
    }
  }

  const setPage = (newPage: number) => {
    page.value = newPage
  }

  const clearCurrentProject = () => {
    currentProject.value = null
    comments.value = []
  }

  return {
    // State
    projects,
    currentProject,
    comments,
    loading,
    total,
    page,
    pageSize,
    // Getters
    hasProjects,
    isLoading,
    // Actions
    fetchPublicProjects,
    fetchPublicProject,
    toggleLike,
    toggleFavorite,
    fetchProjectComments,
    addComment,
    downloadProject,
    publishProject,
    setPage,
    clearCurrentProject
  }
})