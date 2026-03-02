from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.models.project import Project
from app.schemas.user import UserUpdate, UserResponse, PasswordChange
from app.core.security import (
    get_current_user,
    get_password_hash,
    verify_password,
    require_admin,
)

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_my_info(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_my_info(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user_data.username and user_data.username != current_user.username:
        existing_user = db.query(User).filter(User.username == user_data.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该用户名已被使用"
            )
        current_user.username = user_data.username
    
    if user_data.phone is not None:
        current_user.phone = user_data.phone
    
    if user_data.avatar_url is not None:
        current_user.avatar_url = user_data.avatar_url
    
    if user_data.gender is not None:
        if user_data.gender not in ["male", "female", "secret"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的性别值"
            )
        current_user.gender = user_data.gender
    
    if user_data.bio is not None:
        current_user.bio = user_data.bio
    
    if user_data.preferences is not None:
        current_user.preferences = user_data.preferences
    
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.put("/me/password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_password(password_data.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码错误"
        )
    
    current_user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()
    
    return {"message": "密码修改成功"}


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_info(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return user


@router.put("/{user_id}/role")
async def update_user_role(
    user_id: int,
    role: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    if role not in ["admin", "creator", "viewer"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的角色类型"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    user.role = role
    db.commit()
    db.refresh(user)
    
    return {"message": "角色更新成功", "user": UserResponse.from_orm(user)}


@router.put("/{user_id}/status")
async def update_user_status(
    user_id: int,
    is_active: bool,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能禁用当前登录的管理员账号"
        )
    
    user.is_active = is_active
    db.commit()
    db.refresh(user)
    
    status_text = "启用" if is_active else "禁用"
    return {"message": f"账号{status_text}成功", "user": UserResponse.from_orm(user)}


@router.get("/{user_id}/projects")
async def get_user_projects(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    projects = db.query(Project).filter(Project.user_id == user_id).all()
    return projects


@router.get("/public/{user_id}")
async def get_public_user_info(
    user_id: int,
    db: Session = Depends(get_db)
):
    """获取用户公共信息和其发布的公共项目"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 获取用户发布的公共项目
    projects = db.query(Project).filter(
        Project.user_id == user_id,
        Project.is_public == True,
        Project.status == "completed"
    ).all()
    
    # 添加用户名信息到项目
    for project in projects:
        project.username = user.username
    
    return {
        "user": user,
        "projects": projects
    }


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除当前登录的管理员账号"
        )
    
    db.delete(user)
    db.commit()
    
    return {"message": "用户删除成功"}


@router.get("/", response_model=list[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    role: str = None,
    is_active: bool = None,
    search: str = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    query = db.query(User)
    
    if role:
        query = query.filter(User.role == role)
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    if search:
        query = query.filter(
            User.username.contains(search) | 
            User.email.contains(search)
        )
    
    users = query.offset(skip).limit(limit).all()
    return users
