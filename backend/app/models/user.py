"""
用户 & 角色模型
- users：后台登录用户
- roles：角色（如 admin）
- user_role：用户-角色多对多关联
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Table,
    func,
)
from sqlalchemy.orm import relationship

from app.database import Base


# ---------- 用户-角色关联表 ----------

user_role = Table(
    "user_role",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, comment="用户ID"),
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True, comment="角色ID"),
)


# ---------- 用户表 ----------

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="用户ID")
    username = Column(String(50), unique=True, nullable=False, index=True, comment="登录用户名")
    password_hash = Column(String(255), nullable=False, comment="密码哈希（bcrypt）")
    nickname = Column(String(50), nullable=True, comment="显示昵称")
    avatar = Column(String(500), nullable=True, comment="头像URL")
    is_active = Column(Boolean, default=True, nullable=False, comment="是否启用")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关联
    roles = relationship("Role", secondary=user_role, back_populates="users", lazy="selectin")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"


# ---------- 角色表 ----------

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="角色ID")
    name = Column(String(50), unique=True, nullable=False, comment="角色名称（如 admin, editor）")
    description = Column(String(200), nullable=True, comment="角色描述")

    # 关联
    users = relationship("User", secondary=user_role, back_populates="roles", lazy="selectin")

    def __repr__(self):
        return f"<Role(id={self.id}, name={self.name})>"
