import apiClient from './client'
import type { UserPublicResponse } from '@/types/user'

export const userApi = {
  // 获取用户公共信息和其发布的公共项目
  getPublicUserInfo(userId: number) {
    return apiClient.get<UserPublicResponse>(`/users/public/${userId}`)
  }
}

export default userApi
