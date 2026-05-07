"""
认证接口路由
- POST /auth/login    登录获取 Token
- GET  /auth/me       获取当前用户信息
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import settings
from app.schemas.common import BaseResponse
from app.schemas.auth import LoginRequest, TokenData, UserInfo
from app.crud.auth import authenticate_user
from app.utils.security import create_access_token
from app.deps.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["认证管理"])


@router.post(
    "/login",
    response_model=BaseResponse[TokenData],
    summary="用户登录",
    description="使用用户名和密码登录，返回 JWT 访问令牌。",
)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    用户登录接口。
    - 校验用户名密码
    - 成功返回 access_token，有效期 24 小时
    """
    user = authenticate_user(db, request.username, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    # 生成 Token
    access_token = create_access_token(
        data={"sub": user.id, "username": user.username}
    )

    return BaseResponse(
        message="登录成功",
        data=TokenData(
            access_token=access_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # 转为秒
        ),
    )


@router.get(
    "/me",
    response_model=BaseResponse[UserInfo],
    summary="获取当前用户信息",
    description="根据请求头中的 JWT 令牌返回当前登录用户的基本信息。",
)
def get_me(current_user: User = Depends(get_current_user)):
    """
    获取当前登录用户信息。
    - 需要携带有效的 Bearer Token
    """
    # 从 User 对象提取角色名列表
    role_names = [role.name for role in current_user.roles]

    return BaseResponse(
        data=UserInfo(
            id=current_user.id,
            username=current_user.username,
            nickname=current_user.nickname,
            avatar=current_user.avatar,
            is_active=current_user.is_active,
            roles=role_names,
            created_at=current_user.created_at,
        )
    )
