from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class FileTypeEnum(str, Enum):
    model = "model"
    texture = "texture"
    animation = "animation"


class FileUploadResponse(BaseModel):
    file_id: str = Field(..., description="文件唯一ID")
    url: str = Field(..., description="文件访问URL")
    stored_name: str = Field(..., description="存储文件名")
    object_name: str = Field(..., description="MinIO对象名称")
    original_name: str = Field(..., description="原始文件名")
    size: int = Field(..., description="文件大小(字节)")
    mime_type: str = Field(..., description="MIME类型")
    type: str = Field(..., description="文件类型分类")
    bucket: str = Field(..., description="存储桶名称")


class FileUploadSuccess(BaseModel):
    success: bool = True
    data: FileUploadResponse


class FileUploadError(BaseModel):
    success: bool = False
    error: str


class PresignedUrlResponse(BaseModel):
    url: str = Field(..., description="预签名下载URL")
    expires_in: int = Field(default=3600, description="URL有效期(秒)")


class FileDeleteResponse(BaseModel):
    success: bool
    message: str
