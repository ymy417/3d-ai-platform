from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, projects, appeals, moderation, admin, files

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户"])
api_router.include_router(projects.router, prefix="/projects", tags=["项目"])
api_router.include_router(appeals.router, prefix="/appeals", tags=["申诉"])
api_router.include_router(moderation.router, prefix="/moderation", tags=["内容审核"])
api_router.include_router(admin.router, prefix="/admin", tags=["管理员"])
api_router.include_router(files.router, prefix="/files", tags=["文件上传"])
