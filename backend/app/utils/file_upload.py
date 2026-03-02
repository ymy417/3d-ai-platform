from minio import Minio
from minio.error import S3Error
from app.core.config import settings
from typing import Optional, Tuple, Dict, Any
from fastapi import UploadFile
import uuid
import os
import io
from datetime import timedelta

DEFAULT_BUCKET = "user-projects"

ALLOWED_EXTENSIONS: Dict[str, list] = {
    "model": [".obj", ".fbx", ".gltf", ".glb"],
    "texture": [".png", ".jpg", ".jpeg", ".hdr", ".webp"],
    "animation": [".anim", ".fbx"]
}

MIME_TYPES: Dict[str, str] = {
    ".obj": "application/octet-stream",
    ".fbx": "application/octet-stream",
    ".gltf": "model/gltf+json",
    ".glb": "model/gltf-binary",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".hdr": "image/vnd.radiance",
    ".webp": "image/webp",
    ".anim": "application/octet-stream"
}

MAX_FILE_SIZES: Dict[str, int] = {
    "model": 100 * 1024 * 1024,
    "texture": 20 * 1024 * 1024,
    "animation": 50 * 1024 * 1024
}

minio_client = Minio(
    settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=settings.MINIO_SECURE
)

def ensure_bucket_exists(bucket_name: str = DEFAULT_BUCKET) -> bool:
    try:
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)
            return True
        return True
    except S3Error as e:
        print(f"Error creating bucket: {e}")
        return False

def get_file_extension(filename: str) -> str:
    return os.path.splitext(filename)[1].lower()

def validate_file_type(filename: str, file_type: str) -> Tuple[bool, str]:
    ext = get_file_extension(filename)
    if file_type not in ALLOWED_EXTENSIONS:
        return False, f"Invalid file type category: {file_type}"
    
    if ext not in ALLOWED_EXTENSIONS[file_type]:
        allowed = ", ".join(ALLOWED_EXTENSIONS[file_type])
        return False, f"File extension '{ext}' not allowed for type '{file_type}'. Allowed: {allowed}"
    
    return True, ""

def validate_file_size(file_size: int, file_type: str) -> Tuple[bool, str]:
    if file_type not in MAX_FILE_SIZES:
        return False, f"Unknown file type: {file_type}"
    
    if file_size > MAX_FILE_SIZES[file_type]:
        max_mb = MAX_FILE_SIZES[file_type] / (1024 * 1024)
        return False, f"File size exceeds maximum allowed ({max_mb}MB) for type '{file_type}'"
    
    return True, ""

def upload_file_stream(
    file: UploadFile,
    user_id: int,
    file_type: str,
    bucket_name: str = DEFAULT_BUCKET
) -> Tuple[bool, Dict[str, Any]]:
    ensure_bucket_exists(bucket_name)
    
    is_valid_type, type_error = validate_file_type(file.filename or "", file_type)
    if not is_valid_type:
        return False, {"error": type_error}
    
    file_content = file.file.read()
    file_size = len(file_content)
    
    is_valid_size, size_error = validate_file_size(file_size, file_type)
    if not is_valid_size:
        return False, {"error": size_error}
    
    ext = get_file_extension(file.filename or "")
    stored_name = f"{uuid.uuid4().hex}{ext}"
    
    type_folder = f"{file_type}s"
    object_name = f"{type_folder}/{user_id}/{stored_name}"
    
    content_type = MIME_TYPES.get(ext, "application/octet-stream")
    
    try:
        minio_client.put_object(
            bucket_name=bucket_name,
            object_name=object_name,
            data=io.BytesIO(file_content),
            length=file_size,
            content_type=content_type
        )
        
        file_url = f"http://{settings.MINIO_ENDPOINT}/{bucket_name}/{object_name}"
        
        return True, {
            "file_id": uuid.uuid4().hex,
            "url": file_url,
            "stored_name": stored_name,
            "object_name": object_name,
            "original_name": file.filename,
            "size": file_size,
            "mime_type": content_type,
            "type": file_type,
            "bucket": bucket_name
        }
    except S3Error as e:
        return False, {"error": f"Upload failed: {str(e)}"}

def upload_file(
    bucket_name: str,
    file_path: str,
    content_type: str,
    object_name: Optional[str] = None
) -> Tuple[str, str]:
    ensure_bucket_exists(bucket_name)
    
    file_ext = os.path.splitext(file_path)[1]
    if object_name is None:
        object_name = f"{uuid.uuid4().hex}{file_ext}"
    
    minio_client.fput_object(
        bucket_name=bucket_name,
        object_name=object_name,
        file_path=file_path,
        content_type=content_type
    )
    
    file_url = f"http://{settings.MINIO_ENDPOINT}/{bucket_name}/{object_name}"
    return file_url, object_name

def get_presigned_url(
    object_name: str,
    bucket_name: str = DEFAULT_BUCKET,
    expires: int = 3600
) -> Optional[str]:
    try:
        url = minio_client.presigned_get_object(
            bucket_name=bucket_name,
            object_name=object_name,
            expires=timedelta(seconds=expires)
        )
        return url
    except S3Error as e:
        print(f"Error generating presigned URL: {e}")
        return None

def delete_file(
    object_name: str,
    bucket_name: str = DEFAULT_BUCKET
) -> Tuple[bool, str]:
    try:
        minio_client.remove_object(bucket_name, object_name)
        return True, "File deleted successfully"
    except S3Error as e:
        return False, f"Delete failed: {str(e)}"

def file_exists(
    object_name: str,
    bucket_name: str = DEFAULT_BUCKET
) -> bool:
    try:
        minio_client.stat_object(bucket_name, object_name)
        return True
    except S3Error:
        return False
