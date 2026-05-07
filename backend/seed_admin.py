"""
创建默认管理员账号
首次运行：python seed_admin.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from passlib.context import CryptContext
from app.database import SessionLocal
from app.models import User, Role

# 密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def seed_admin():
    db = SessionLocal()
    try:
        # 检查是否已存在
        existing = db.query(User).filter(User.username == "admin").first()
        if existing:
            print(f"⚠️  管理员账号已存在: {existing.username}")
            return

        # 创建管理员用户
        admin = User(
            username="admin",
            password_hash=pwd_context.hash("admin123"),
            nickname="系统管理员",
            is_active=True,
        )
        db.add(admin)
        db.flush()

        # 分配 admin 角色
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        if admin_role:
            admin.roles.append(admin_role)

        db.commit()
        print("✅ 管理员账号创建成功！")
        print(f"   用户名: admin")
        print(f"   密码:   admin123")
        print(f"   角色:   admin")
        print("⚠️  请登录后立即修改密码！")

    except Exception as e:
        db.rollback()
        print(f"❌ 创建失败: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_admin()
