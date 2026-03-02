from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.db.session import get_db
from app.models.project import Project, Like, Favorite, Comment
from app.models.user import User
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectStatusUpdate,
    ProjectResponse,
    ProjectListResponse,
    CommentCreate,
    CommentResponse,
)
from app.core.security import get_current_user, require_admin

router = APIRouter()


@router.get("/", response_model=ProjectListResponse)
async def list_projects(
    status: Optional[str] = Query(None, description="按状态筛选"),
    search: Optional[str] = Query(None, description="按名称搜索"),
    sort_by: str = Query("created_at", description="排序字段"),
    sort_order: str = Query("desc", description="排序方向"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(12, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Project).filter(Project.user_id == current_user.id)
    
    # 状态筛选
    if status:
        query = query.filter(Project.status == status)
    
    # 名称搜索
    if search:
        query = query.filter(Project.name.contains(search))
    
    # 排序
    if sort_order == "desc":
        query = query.order_by(getattr(Project, sort_by).desc())
    else:
        query = query.order_by(getattr(Project, sort_by).asc())
    
    # 分页
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return ProjectListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_project = Project(
        name=project_data.name,
        description=project_data.description,
        user_id=current_user.id,
        status="draft",
        model_data={
            "model": None,
            "textures": [],
            "skeleton": None,
            "animations": [],
            "render_settings": {}
        },
        storage_paths={
            "minio_bucket": "user-projects",
            "model_key": None,
            "texture_keys": [],
            "animation_keys": []
        }
    )
    
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    
    return new_project


# ========== 管理员接口 ==========

@router.get("/all", response_model=list[ProjectResponse])
async def get_all_projects(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    is_public: Optional[bool] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """管理员获取所有作品列表"""
    query = db.query(Project)
    
    if status:
        query = query.filter(Project.status == status)
    
    if is_public is not None:
        query = query.filter(Project.is_public == is_public)
    
    projects = query.offset(skip).limit(limit).all()
    return projects


@router.put("/{project_id}/public", response_model=ProjectResponse)
async def toggle_project_public(
    project_id: int,
    is_public: bool,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """管理员设置作品公开/私密状态"""
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    project.is_public = is_public
    db.commit()
    db.refresh(project)
    
    return project


# ========== 公共画廊接口 ==========

@router.get("/public/list", response_model=ProjectListResponse)
async def list_public_projects(
    search_type: Optional[str] = Query(None, description="搜索类型: project或user"),
    search_value: Optional[str] = Query(None, description="搜索值"),
    sort_by: str = Query("created_at", description="排序字段"),
    sort_order: str = Query("desc", description="排序方向"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(12, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """获取公共项目列表"""
    query = db.query(Project).filter(Project.is_public == True, Project.status == "completed")
    
    # 搜索
    if search_value:
        if search_type == "user":
            # 按作者名称搜索
            user_ids = db.query(User.id).filter(User.username.contains(search_value)).all()
            user_ids = [user[0] for user in user_ids]
            if user_ids:
                query = query.filter(Project.user_id.in_(user_ids))
        else:
            # 按项目名称搜索
            query = query.filter(Project.name.contains(search_value))
    
    # 排序
    if sort_order == "desc":
        query = query.order_by(getattr(Project, sort_by).desc())
    else:
        query = query.order_by(getattr(Project, sort_by).asc())
    
    # 分页
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    
    # 添加用户名信息
    for item in items:
        user = db.query(User).filter(User.id == item.user_id).first()
        if user:
            item.username = user.username
    
    return ProjectListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/public/{project_id}", response_model=ProjectResponse)
async def get_public_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    """获取公共项目详情"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.is_public == True,
        Project.status == "completed"
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在或未公开"
        )
    
    # 添加用户名信息
    user = db.query(User).filter(User.id == project.user_id).first()
    if user:
        project.username = user.username
    
    return project


@router.get("/favorites")
async def get_favorite_projects(
    sort_by: str = Query("created_at", description="排序字段"),
    sort_order: str = Query("desc", description="排序方向"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(12, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户收藏的项目"""
    # 查询用户收藏的项目
    query = db.query(Project).join(Favorite, Project.id == Favorite.project_id).filter(
        Favorite.user_id == current_user.id,
        Project.is_public == True,
        Project.status == "completed"
    )
    
    # 排序
    if sort_order == "desc":
        query = query.order_by(getattr(Project, sort_by).desc())
    else:
        query = query.order_by(getattr(Project, sort_by).asc())
    
    # 分页
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    
    # 添加用户名信息
    for item in items:
        user = db.query(User).filter(User.id == item.user_id).first()
        if user:
            item.username = user.username
    
    return ProjectListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.delete("/bulk")
async def bulk_delete_projects(
    project_ids: List[int] = Query(..., description="项目ID列表"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """批量删除项目"""
    # 验证项目所有权
    projects = db.query(Project).filter(
        Project.id.in_(project_ids),
        Project.user_id == current_user.id
    ).all()
    
    if len(projects) != len(project_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="部分项目不存在或无权删除"
        )
    
    # 删除项目
    for project in projects:
        db.delete(project)
    
    db.commit()
    
    return {"message": f"成功删除 {len(projects)} 个项目"}


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    if project_data.name is not None:
        project.name = project_data.name
    if project_data.description is not None:
        project.description = project_data.description
    
    db.commit()
    db.refresh(project)
    
    return project


@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    db.delete(project)
    db.commit()
    
    return {"message": "项目删除成功"}


@router.put("/{project_id}/status")
async def update_project_status(
    project_id: int,
    status_data: ProjectStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if status_data.status not in ["draft", "processing", "completed", "archived"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的项目状态"
        )
    
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    project.status = status_data.status
    db.commit()
    db.refresh(project)
    
    return {"message": "状态更新成功", "status": project.status}


@router.post("/{project_id}/duplicate", response_model=ProjectResponse)
async def duplicate_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    new_project = Project(
        name=f"{project.name} (副本)",
        description=project.description,
        user_id=current_user.id,
        status="draft",
        model_data=project.model_data.copy() if project.model_data else {},
        storage_paths={
            "minio_bucket": "user-projects",
            "model_key": None,
            "texture_keys": [],
            "animation_keys": []
        }
    )
    
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    
    return new_project


@router.post("/{project_id}/like")
async def toggle_like(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """点赞/取消点赞"""
    # 检查项目是否存在
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    # 检查是否已点赞
    existing_like = db.query(Like).filter(
        Like.user_id == current_user.id,
        Like.project_id == project_id
    ).first()
    
    if existing_like:
        # 取消点赞
        db.delete(existing_like)
        db.commit()
        return {"message": "取消点赞成功", "liked": False}
    else:
        # 添加点赞
        new_like = Like(user_id=current_user.id, project_id=project_id)
        db.add(new_like)
        db.commit()
        return {"message": "点赞成功", "liked": True}


@router.post("/{project_id}/favorite")
async def toggle_favorite(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """收藏/取消收藏"""
    # 检查项目是否存在
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    # 检查是否已收藏
    existing_favorite = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.project_id == project_id
    ).first()
    
    if existing_favorite:
        # 取消收藏
        db.delete(existing_favorite)
        db.commit()
        return {"message": "取消收藏成功", "favorited": False}
    else:
        # 添加收藏
        new_favorite = Favorite(user_id=current_user.id, project_id=project_id)
        db.add(new_favorite)
        db.commit()
        return {"message": "收藏成功", "favorited": True}


@router.get("/{project_id}/comments", response_model=List[CommentResponse])
async def get_project_comments(
    project_id: int,
    db: Session = Depends(get_db)
):
    """获取项目评论"""
    # 检查项目是否存在
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    comments = db.query(Comment).filter(
        Comment.project_id == project_id
    ).order_by(Comment.created_at.desc()).all()
    
    # 添加用户名信息
    for comment in comments:
        user = db.query(User).filter(User.id == comment.user_id).first()
        if user:
            comment.username = user.username
    
    return comments


@router.post("/{project_id}/comments", response_model=CommentResponse)
async def add_comment(
    project_id: int,
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """添加评论"""
    # 检查项目是否存在
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    new_comment = Comment(
        user_id=current_user.id,
        project_id=project_id,
        content=comment_data.content
    )
    
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    
    # 添加用户名信息
    new_comment.username = current_user.username
    
    return new_comment


@router.delete("/{project_id}/comments/{comment_id}")
async def delete_comment(
    project_id: int,
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除评论"""
    # 检查评论是否存在且属于当前用户
    comment = db.query(Comment).filter(
        Comment.id == comment_id,
        Comment.project_id == project_id,
        Comment.user_id == current_user.id
    ).first()
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评论不存在或无权删除"
        )
    
    db.delete(comment)
    db.commit()
    
    return {"message": "评论删除成功"}


@router.get("/{project_id}/download")
async def download_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """下载项目"""
    # 检查项目是否存在
    project = db.query(Project).filter(
        Project.id == project_id,
        (Project.user_id == current_user.id) | (Project.is_public == True)
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    # 检查是否允许下载
    if not project.allow_download and project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="该项目不允许下载"
        )
    
    # 这里应该返回文件下载链接或文件内容
    # 暂时返回项目信息
    return {"message": "下载功能开发中", "project_id": project_id, "name": project.name}


@router.put("/{project_id}/publish")
async def publish_project(
    project_id: int,
    is_public: bool = Query(..., description="是否公开"),
    allow_download: Optional[bool] = Query(None, description="是否允许下载"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """发布/取消发布项目"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    project.is_public = is_public
    if allow_download is not None:
        project.allow_download = allow_download
    
    # 当项目设置为公开时，自动将状态设置为completed
    if is_public and project.status != "completed":
        project.status = "completed"
    
    db.commit()
    db.refresh(project)
    
    return {"message": "发布状态更新成功", "is_public": project.is_public, "allow_download": project.allow_download, "status": project.status}
