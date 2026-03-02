from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="项目名称")
    description: Optional[str] = Field(None, max_length=1000, description="项目描述")


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="项目名称")
    description: Optional[str] = Field(None, max_length=1000, description="项目描述")


class ProjectStatusUpdate(BaseModel):
    status: str = Field(..., description="项目状态: draft/processing/completed/archived")


class ProjectResponse(ProjectBase):
    id: int
    user_id: int
    username: Optional[str] = None
    status: str
    model_data: Dict[str, Any]
    storage_paths: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    items: List[ProjectResponse]
    total: int
    page: int
    page_size: int


class ProjectFilter(BaseModel):
    status: Optional[str] = Field(None, description="按状态筛选")
    search: Optional[str] = Field(None, description="按名称搜索")
    sort_by: Optional[str] = Field("created_at", description="排序字段")
    sort_order: Optional[str] = Field("desc", description="排序方向: asc/desc")


class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000, description="评论内容")


class CommentResponse(BaseModel):
    id: int
    user_id: int
    username: Optional[str] = None
    project_id: int
    content: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
