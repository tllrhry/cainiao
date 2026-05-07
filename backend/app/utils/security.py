"""
安全工具函数
- 密码哈希 / 校验（bcrypt + passlib）
- JWT 生成 / 解码（python-jose）
"""

from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import jwt, JWTError

from app.config import settings

# ---------- 密码上下文 ----------

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """对明文密码做 bcrypt 哈希"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """校验明文密码与哈希是否匹配"""
    return pwd_context.verify(plain_password, hashed_password)


# ---------- JWT ----------


def create_access_token(data: dict) -> str:
    """
    生成 JWT 访问令牌。
    data 至少包含 {"sub": user_id, "username": "xxx"}
    注意：JWT 标准要求 sub 为字符串，encode 时自动转换。
    """
    to_encode = data.copy()
    # JWT 规范要求 sub 必须是字符串
    if "sub" in to_encode:
        to_encode["sub"] = str(to_encode["sub"])
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict:
    """
    解码 JWT 令牌，返回 payload 字典。
    如果令牌无效或过期，抛出 JWTError。
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
