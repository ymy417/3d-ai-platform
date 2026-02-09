from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="3D AI角色创作平台 - 后端API",
    description="AI 3D模型生成、用户管理、对象存储服务接口",
    version="1.0.0"
)

# 跨域配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 健康检查接口
@app.get("/", tags=["健康检查"])
def health_check():
    return {"status": "ok", "message": "3D AI Platform Backend Running"}

@app.get("/api/v1/health", tags=["健康检查"])
def api_health():
    return {"status": "running", "version": "v1"}
