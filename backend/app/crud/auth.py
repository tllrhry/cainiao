"""
认证相关 数据访问层（CRUD）
- 用户查询
- 用户认证
"""

from sqlalchemy.orm import Session

from app.models.user import User
from app.utils.security import verify_password


def get_user_by_username(db: Session, username: str) -> User | None:
    """按用户名查找用户"""
    return db.query(User).filter(User.username == username).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """按 ID 查找用户"""
    return db.query(User).filter(User.id == user_id).first()


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    """
    认证用户：校验用户名 + 密码。
    成功返回 User 对象，失败返回 None。
    """
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    if not user.is_active:
        return None
    return user
