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
from app.api.v1.routers import upload as upload_router
from app.api.v1.routers import carousels as carousels_router
from app.api.v1.routers import articles as articles_router
from app.api.v1.routers import cases as cases_router
from app.api.v1.routers import company as company_router
from app.api.v1.routers import stats as stats_router

# 创建应用实例
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="菜鸟设计企业门户网站 API",
)

# CORS 中间件
# 注意：allow_credentials=True 时，allow_origins 不能用通配符 "*"
# 需要认证的请求（Authorization header）走 token 机制，无需 cookie，故设为 False
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # 允许所有来源（浏览器预检）
    allow_credentials=False,       # 不使用 cookie 凭证，token 在 Authorization header 中传递
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务（上传的文件，目录改到 static/uploads）
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount(f"/{settings.UPLOAD_DIR}", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# ===================== 注册路由 =====================

# 认证模块
app.include_router(auth_router.router, prefix="/api/v1")

# 文件上传
app.include_router(upload_router.router, prefix="/api/v1")

# 轮播图管理
app.include_router(carousels_router.router, prefix="/api/v1")

# 文章管理
app.include_router(articles_router.router, prefix="/api/v1")

# 案例管理
app.include_router(cases_router.router, prefix="/api/v1")

# 公司信息
app.include_router(company_router.router, prefix="/api/v1")

# 仪表盘统计
app.include_router(stats_router.router, prefix="/api/v1")


# ---------- 根路径 & 健康检查 ----------

@app.get("/")
async def root():
    """根路径 - 健康检查"""
    return {"message": f"欢迎访问 {settings.APP_NAME} API", "version": settings.APP_VERSION}


@app.get("/api/health")
async def health_check():
    """健康检查接口"""
    return {"status": "ok", "service": settings.APP_NAME}
