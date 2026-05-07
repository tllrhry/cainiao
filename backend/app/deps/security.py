"""
安全依赖注入
- get_current_user：从 JWT 解析当前用户
- require_admin：校验管理员角色
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError

from app.database import get_db
from app.models.user import User
from app.crud.auth import get_user_by_id
from app.utils.security import decode_access_token

# HTTP Bearer 安全方案（从请求头提取 Authorization: Bearer <token>）
security_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    解析 JWT，返回当前登录用户。
    - 未提供 / 无效 / 过期令牌 → 401
    - 用户不存在或已禁用 → 401 / 403
    """
    token = credentials.credentials

    # 解码 JWT
    try:
        payload = decode_access_token(token)
        raw_sub = payload.get("sub")
        if raw_sub is None:
            user_id = None
        else:
            user_id = int(raw_sub)  # JWT sub 存为字符串，转回整数
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证凭证：缺少用户标识",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证：令牌解析失败",
        )

    # 查库获取用户
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用，请联系管理员",
        )

    return user


def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    管理员权限校验 —— 依赖 get_current_user，额外检查是否包含 admin 角色。
    非 admin 角色 → 403。
    """
    if not any(role.name == "admin" for role in current_user.roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限",
        )
    return current_user
