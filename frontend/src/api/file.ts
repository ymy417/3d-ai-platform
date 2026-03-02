import client from './client'
import type { AxiosProgressEvent } from 'axios'

export type FileType = 'model' | 'texture' | 'animation'

export interface UploadResponse {
  file_id: string
  url: string
  stored_name: string
  object_name: string
  original_name: string
  size: number
  mime_type: string
  type: FileType
  bucket: string
}

export interface UploadSuccessResponse {
  success: boolean
  data: UploadResponse
}

export interface PresignedUrlResponse {
  url: string
  expires_in: number
}

export interface FileDeleteResponse {
  success: boolean
  message: string
}

export interface UploadOptions {
  type: FileType
  projectId?: number
  onProgress?: (progress: number) => void
}

export const fileApi = {
  async uploadFile(file: File, options: UploadOptions): Promise<UploadSuccessResponse> {
    const formData = new FormData()
    formData.append('file', file)
    
    const params = new URLSearchParams()
    params.append('type', options.type)
    if (options.projectId) {
      params.append('project_id', options.projectId.toString())
    }
    
    const response = await client.post<UploadSuccessResponse>(
      `/files/upload?${params.toString()}`,
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (progressEvent: AxiosProgressEvent) => {
          if (options.onProgress && progressEvent.total) {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
            options.onProgress(progress)
          }
        }
      }
    )
    
    return response.data
  },

  async uploadToProject(projectId: number, file: File, type: FileType, onProgress?: (progress: number) => void): Promise<UploadSuccessResponse> {
    const formData = new FormData()
    formData.append('file', file)
    
    const params = new URLSearchParams()
    params.append('type', type)
    
    const response = await client.post<UploadSuccessResponse>(
      `/files/upload-to-project/${projectId}?${params.toString()}`,
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (progressEvent: AxiosProgressEvent) => {
          if (onProgress && progressEvent.total) {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
            onProgress(progress)
          }
        }
      }
    )
    
    return response.data
  },

  async getPresignedUrl(objectName: string, bucket?: string, expires?: number): Promise<PresignedUrlResponse> {
    const params = new URLSearchParams()
    params.append('object_name', objectName)
    if (bucket) params.append('bucket', bucket)
    if (expires) params.append('expires', expires.toString())
    
    const response = await client.get<PresignedUrlResponse>(`/files/presigned-url?${params.toString()}`)
    return response.data
  },

  async deleteFile(objectName: string, bucket?: string): Promise<FileDeleteResponse> {
    const params = new URLSearchParams()
    if (bucket) params.append('bucket', bucket)
    
    const response = await client.delete<FileDeleteResponse>(`/files/${encodeURIComponent(objectName)}?${params.toString()}`)
    return response.data
  }
}

export function getFileTypeFromExtension(filename: string): FileType {
  const ext = filename.split('.').pop()?.toLowerCase() || ''
  
  const modelExtensions = ['obj', 'fbx', 'gltf', 'glb']
  const textureExtensions = ['png', 'jpg', 'jpeg', 'hdr', 'webp']
  const animationExtensions = ['anim']
  
  if (modelExtensions.includes(ext)) return 'model'
  if (textureExtensions.includes(ext)) return 'texture'
  if (animationExtensions.includes(ext)) return 'animation'
  
  return 'model'
}

export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}
