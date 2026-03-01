from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100, description="密码")


class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., description="密码")


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="用户名")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    avatar_url: Optional[str] = Field(None, max_length=500, description="头像URL")
    preferences: Optional[dict] = Field(None, description="用户偏好设置")


class UserResponse(UserBase):
    id: int
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    role: str
    is_active: bool
    is_verified: bool
    preferences: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    user_id: Optional[int] = None
    role: Optional[str] = None


class PasswordChange(BaseModel):
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=100, description="新密码")
