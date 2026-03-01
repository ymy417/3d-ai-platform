import client from './client'
import type { User, UserCreate, UserLogin, UserUpdate, Token, PasswordChange } from '@/types/user'

export const authApi = {
  async register(data: UserCreate): Promise<User> {
    const response = await client.post<User>('/auth/register', data)
    return response.data
  },

  async login(data: UserLogin): Promise<Token> {
    const response = await client.post<Token>('/auth/login', data)
    return response.data
  },

  async logout(): Promise<void> {
    await client.post('/auth/logout')
  },

  async getCurrentUser(): Promise<User> {
    const response = await client.get<User>('/auth/me')
    return response.data
  },

  async updateProfile(data: UserUpdate): Promise<User> {
    const response = await client.put<User>('/users/me', data)
    return response.data
  },

  async changePassword(data: PasswordChange): Promise<void> {
    await client.put('/users/me/password', data)
  },
}
