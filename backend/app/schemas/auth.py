"""
认证模块 Pydantic Schema
- 请求体：登录表单
- 响应体：Token、用户信息
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ========== 请求体 ==========


class LoginRequest(BaseModel):
    """登录请求"""

    username: str = Field(..., min_length=1, max_length=50, description="用户名")
    password: str = Field(..., min_length=1, max_length=128, description="密码")


# ========== 响应体 ==========


class TokenData(BaseModel):
    """Token 响应数据"""

    access_token: str = Field(..., description="JWT 访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间（秒）")


class UserInfo(BaseModel):
    """用户基本信息（get /me 返回）"""

    id: int
    username: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    is_active: bool
    roles: list[str] = Field(default_factory=list, description="角色列表（如 ['admin']）")
    created_at: datetime

    model_config = {"from_attributes": True}
