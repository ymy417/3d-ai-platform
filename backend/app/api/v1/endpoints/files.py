from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.db.session import get_db
from app.models.user import User
from app.models.project import Project
from app.schemas.file import (
    FileUploadResponse,
    FileUploadSuccess,
    FileUploadError,
    PresignedUrlResponse,
    FileDeleteResponse,
    FileTypeEnum
)
from app.core.security import get_current_user
from app.utils.file_upload import (
    upload_file_stream,
    get_presigned_url,
    delete_file,
    DEFAULT_BUCKET
)

router = APIRouter()


@router.post("/upload", response_model=FileUploadSuccess, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(..., description="要上传的文件"),
    type: FileTypeEnum = Query(..., description="文件类型: model/texture/animation"),
    project_id: Optional[int] = Query(None, description="关联项目ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if project_id:
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == current_user.id
        ).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="项目不存在或无权限"
            )
    
    success, result = upload_file_stream(
        file=file,
        user_id=current_user.id,
        file_type=type.value
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "上传失败")
        )
    
    return FileUploadSuccess(
        success=True,
        data=FileUploadResponse(
            file_id=result["file_id"],
            url=result["url"],
            stored_name=result["stored_name"],
            object_name=result["object_name"],
            original_name=result["original_name"],
            size=result["size"],
            mime_type=result["mime_type"],
            type=result["type"],
            bucket=result["bucket"]
        )
    )


@router.get("/presigned-url", response_model=PresignedUrlResponse)
async def get_download_url(
    object_name: str = Query(..., description="MinIO对象名称"),
    bucket: str = Query(DEFAULT_BUCKET, description="存储桶名称"),
    expires: int = Query(3600, ge=60, le=86400, description="URL有效期(秒)"),
    current_user: User = Depends(get_current_user)
):
    url = get_presigned_url(
        object_name=object_name,
        bucket_name=bucket,
        expires=expires
    )
    
    if not url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在或无法生成下载链接"
        )
    
    return PresignedUrlResponse(url=url, expires_in=expires)


@router.delete("/{object_name:path}", response_model=FileDeleteResponse)
async def delete_uploaded_file(
    object_name: str,
    bucket: str = Query(DEFAULT_BUCKET, description="存储桶名称"),
    current_user: User = Depends(get_current_user)
):
    path_parts = object_name.split("/")
    if len(path_parts) >= 3:
        try:
            folder_user_id = int(path_parts[1])
            if folder_user_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="无权限删除此文件"
                )
        except ValueError:
            pass
    
    success, message = delete_file(object_name=object_name, bucket_name=bucket)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return FileDeleteResponse(success=True, message=message)


@router.post("/upload-to-project/{project_id}", response_model=FileUploadSuccess)
async def upload_file_to_project(
    project_id: int,
    file: UploadFile = File(..., description="要上传的文件"),
    type: FileTypeEnum = Query(..., description="文件类型: model/texture/animation"),
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
            detail="项目不存在或无权限"
        )
    
    success, result = upload_file_stream(
        file=file,
        user_id=current_user.id,
        file_type=type.value
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "上传失败")
        )
    
    storage_paths = project.storage_paths or {}
    object_name = result["object_name"]
    
    if type == FileTypeEnum.model:
        storage_paths["model_key"] = object_name
    elif type == FileTypeEnum.texture:
        texture_keys = storage_paths.get("texture_keys", [])
        texture_keys.append(object_name)
        storage_paths["texture_keys"] = texture_keys
    elif type == FileTypeEnum.animation:
        animation_keys = storage_paths.get("animation_keys", [])
        animation_keys.append(object_name)
        storage_paths["animation_keys"] = animation_keys
    
    project.storage_paths = storage_paths
    db.commit()
    
    return FileUploadSuccess(
        success=True,
        data=FileUploadResponse(
            file_id=result["file_id"],
            url=result["url"],
            stored_name=result["stored_name"],
            object_name=result["object_name"],
            original_name=result["original_name"],
            size=result["size"],
            mime_type=result["mime_type"],
            type=result["type"],
            bucket=result["bucket"]
        )
    )
