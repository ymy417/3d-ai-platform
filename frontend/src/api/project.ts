import apiClient from './client'
import type {
  Project,
  ProjectListResponse,
  ProjectCreateRequest,
  ProjectUpdateRequest,
  ProjectStatusUpdateRequest,
  ProjectFilterParams,
  Comment,
  CommentCreateRequest,
  LikeResponse,
  FavoriteResponse,
  DownloadResponse,
  PublishResponse
} from '@/types/project'

export const projectApi = {
  // 获取项目列表
  getProjects(params?: ProjectFilterParams) {
    return apiClient.get<ProjectListResponse>('/projects/', { params })
  },

  // 创建项目
  createProject(data: ProjectCreateRequest) {
    return apiClient.post<Project>('/projects/', data)
  },

  // 获取项目详情
  getProject(id: number) {
    return apiClient.get<Project>(`/projects/${id}`)
  },

  // 更新项目
  updateProject(id: number, data: ProjectUpdateRequest) {
    return apiClient.put<Project>(`/projects/${id}`, data)
  },

  // 删除项目
  deleteProject(id: number) {
    return apiClient.delete(`/projects/${id}`)
  },

  // 更新项目状态
  updateProjectStatus(id: number, data: ProjectStatusUpdateRequest) {
    return apiClient.put(`/projects/${id}/status`, data)
  },

  // 复制项目
  duplicateProject(id: number) {
    return apiClient.post<Project>(`/projects/${id}/duplicate`)
  },

  // ========== 公共画廊接口 ==========

  // 获取公共项目列表
  getPublicProjects(params?: ProjectFilterParams) {
    return apiClient.get<ProjectListResponse>('/projects/public/list', { params })
  },

  // 获取公共项目详情
  getPublicProject(id: number) {
    return apiClient.get<Project>(`/projects/public/${id}`)
  },

  // 点赞/取消点赞
  toggleLike(id: number) {
    return apiClient.post<LikeResponse>(`/projects/${id}/like`)
  },

  // 收藏/取消收藏
  toggleFavorite(id: number) {
    return apiClient.post<FavoriteResponse>(`/projects/${id}/favorite`)
  },

  // 获取项目评论
  getProjectComments(id: number) {
    return apiClient.get<Comment[]>(`/projects/${id}/comments`)
  },

  // 添加评论
  addComment(id: number, data: CommentCreateRequest) {
    return apiClient.post<Comment>(`/projects/${id}/comments`, data)
  },

  // 下载项目
  downloadProject(id: number) {
    return apiClient.get<DownloadResponse>(`/projects/${id}/download`)
  },

  // 发布/取消发布项目
  publishProject(id: number, isPublic: boolean, allowDownload?: boolean) {
    return apiClient.put<PublishResponse>(`/projects/${id}/publish`, null, {
      params: {
        is_public: isPublic,
        allow_download: allowDownload
      }
    })
  },

  // 批量删除项目
  bulkDeleteProjects(ids: number[]) {
    return apiClient.delete(`/projects/bulk`, {
      params: {
        project_ids: ids
      }
    })
  },

  // 删除评论
  deleteComment(projectId: number, commentId: number) {
    return apiClient.delete(`/projects/${projectId}/comments/${commentId}`)
  },

  // 获取收藏的项目
  getFavoriteProjects(params?: ProjectFilterParams) {
    return apiClient.get<ProjectListResponse>('/projects/favorites', { params })
  }
}

export default projectApi
