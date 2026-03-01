export interface User {
  id: number
  username: string
  email: string
  phone?: string
  avatar_url?: string
  role: 'admin' | 'creator' | 'viewer'
  is_active: boolean
  is_verified: boolean
  preferences?: Record<string, any>
  created_at: string
  updated_at: string
}

export interface UserCreate {
  username: string
  email: string
  password: string
}

export interface UserLogin {
  email: string
  password: string
}

export interface UserUpdate {
  username?: string
  phone?: string
  avatar_url?: string
  preferences?: Record<string, any>
}

export interface Token {
  access_token: string
  token_type: string
  user: User
}

export interface PasswordChange {
  old_password: string
  new_password: string
}
