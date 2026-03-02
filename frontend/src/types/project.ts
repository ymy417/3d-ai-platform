export interface ModelData {
  model: string | null
  textures: string[]
  skeleton: string | null
  animations: string[]
  render_settings: Record<string, any>
}

export interface StoragePaths {
  minio_bucket: string
  model_key: string | null
  texture_keys: string[]
  animation_keys: string[]
}

export interface Project {
  id: number
  name: string
  description: string | null
  user_id: number
  username?: string
  status: 'draft' | 'processing' | 'completed' | 'archived'
  is_public: boolean
  allow_download: boolean
  model_data: ModelData
  storage_paths: StoragePaths
  created_at: string
  updated_at: string
}

export interface ProjectListResponse {
  items: Project[]
  total: number
  page: number
  page_size: number
}

export interface ProjectCreateRequest {
  name: string
  description?: string
}

export interface ProjectUpdateRequest {
  name?: string
  description?: string
}

export interface ProjectStatusUpdateRequest {
  status: 'draft' | 'processing' | 'completed' | 'archived'
}

export interface ProjectFilterParams {
  status?: string
  search_type?: 'project' | 'user'
  search_value?: string
  sort_by?: string
  sort_order?: 'asc' | 'desc'
  page?: number
  page_size?: number
}

export const ProjectStatusMap: Record<string, { label: string; type: string }> = {
  draft: { label: '草稿', type: 'info' },
  processing: { label: '处理中', type: 'warning' },
  completed: { label: '已完成', type: 'success' },
  archived: { label: '已归档', type: 'info' }
}

// 评论相关类型
export interface Comment {
  id: number
  user_id: number
  username?: string
  project_id: number
  content: string
  created_at: string
  updated_at: string
}

export interface CommentCreateRequest {
  content: string
}

// 点赞相关类型
export interface LikeResponse {
  message: string
  liked: boolean
}

// 收藏相关类型
export interface FavoriteResponse {
  message: string
  favorited: boolean
}

// 下载相关类型
export interface DownloadResponse {
  message: string
  project_id: number
  name: string
}

// 发布相关类型
export interface PublishResponse {
  message: string
  is_public: boolean
  allow_download: boolean
  status?: string
}
