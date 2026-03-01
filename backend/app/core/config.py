from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 项目配置
    PROJECT_NAME: str = "3D AI Creation Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # 数据库配置（你的本地环境）
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306  # MySQL默认端口
    MYSQL_USER: str = "root"  # 你的MySQL用户是root
    MYSQL_PASSWORD: str = "670406"  # 你的MySQL密码
    MYSQL_DATABASE: str = "3d_ai_platform"  # 你的数据库名

    MONGODB_URL: str = "mongodb://root:jlsm8a309@localhost:27017/admin"  # 你的MongoDB配置

    # MinIO配置（你的本地环境）
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "admin"
    MINIO_SECRET_KEY: str = "jlsm8a309"
    MINIO_SECURE: bool = False

    # AI服务配置（先留空，后续填）
    STABLE_DIFFUSION_API_KEY: Optional[str] = None
    STABLE_DIFFUSION_BASE_URL: str = "https://api.stability.ai"

    class Config:
        env_file = ".env"  # 支持.env文件覆盖配置

settings = Settings()