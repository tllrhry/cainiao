"""
应用配置模块
通过 pydantic-settings 管理环境变量和配置
"""

from urllib.parse import quote_plus
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""

    # 应用基础
    APP_NAME: str = "菜鸟设计"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # 数据库
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = "Cainiao@123"
    DB_NAME: str = "cainiao_design"

    @property
    def database_url(self) -> str:
        """MySQL 连接地址（PyMySQL 驱动），密码 URL-encode 处理特殊字符"""
        return (
            f"mysql+pymysql://{self.DB_USER}:{quote_plus(self.DB_PASSWORD)}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    # JWT 认证
    SECRET_KEY: str = "cainiao-design-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 小时

    # 文件上传
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB

    # 前端地址（CORS 用）
    FRONTEND_URL: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
