"""
应用主入口
FastAPI 应用实例、CORS 中间件、路由注册
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.config import settings
from app.api.v1.routers import auth as auth_router

# 创建应用实例
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="菜鸟设计企业门户网站 API",
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:80"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务（上传的文件）
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount(f"/{settings.UPLOAD_DIR}", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# ---------- 注册路由 ----------

app.include_router(auth_router.router, prefix="/api/v1")


# ---------- 根路径 & 健康检查 ----------

@app.get("/")
async def root():
    """根路径 - 健康检查"""
    return {"message": f"欢迎访问 {settings.APP_NAME} API", "version": settings.APP_VERSION}


@app.get("/api/health")
async def health_check():
    """健康检查接口"""
    return {"status": "ok", "service": settings.APP_NAME}
