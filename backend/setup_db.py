"""
数据库初始化脚本
- 创建所有表（通过 SQLAlchemy Base.metadata.create_all）
- 插入初始角色（admin）
- 创建默认管理员账号 admin / admin123
"""

import sys
import os

# 确保 backend 目录在 Python 路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from passlib.context import CryptContext
from sqlalchemy import text, inspect
from app.database import engine, SessionLocal, Base
from app.models import User, Role  # noqa: F401 - 触发所有模型注册

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def database_exists() -> bool:
    """检查数据库是否存在"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def create_tables():
    """创建所有表"""
    print("  Creating tables...")
    try:
        # 导入所有模型确保注册到 Base.metadata
        import app.models  # noqa: F401

        Base.metadata.create_all(bind=engine)

        # 列出已创建的表
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"  Tables created: {', '.join(tables)}")
    except Exception as e:
        print(f"  ERROR creating tables: {e}")
        raise


def seed_roles():
    """插入初始角色"""
    db = SessionLocal()
    try:
        # admin 角色
        if not db.query(Role).filter(Role.name == "admin").first():
            db.add(Role(name="admin", description="系统管理员，拥有全部权限"))
            db.commit()
            print("  Role 'admin' created.")
        else:
            print("  Role 'admin' already exists, skipping.")

        # editor 角色（后期用）
        if not db.query(Role).filter(Role.name == "editor").first():
            db.add(Role(name="editor", description="内容编辑，可管理文章和案例"))
            db.commit()
            print("  Role 'editor' created.")
        else:
            print("  Role 'editor' already exists, skipping.")
    finally:
        db.close()


def seed_admin():
    """创建默认管理员账号"""
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == "admin").first()
        if existing:
            print(f"  Admin user already exists: {existing.username}")
            return

        admin = User(
            username="admin",
            password_hash=pwd_context.hash("admin123"),
            nickname="系统管理员",
            is_active=True,
        )
        db.add(admin)
        db.flush()

        admin_role = db.query(Role).filter(Role.name == "admin").first()
        if admin_role:
            admin.roles.append(admin_role)

        db.commit()
        print("  Admin user created: admin / admin123")
    except Exception as e:
        db.rollback()
        print(f"  ERROR creating admin user: {e}")
        raise
    finally:
        db.close()


def main():
    print()
    print("=" * 48)
    print("  Database Setup")
    print("=" * 48)

    # 检查数据库连接
    if not database_exists():
        print()
        print("ERROR: Cannot connect to MySQL.")
        print("Make sure MySQL is running and the database exists:")
        print('  mysql -u root -p"Cainiao@123" -e "CREATE DATABASE IF NOT EXISTS cainiao_design CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"')
        sys.exit(1)

    print("  Database connection: OK")

    # 创建表
    create_tables()

    # 插入角色
    print("  Seeding roles...")
    seed_roles()

    # 创建管理员
    print("  Seeding admin user...")
    seed_admin()

    print()
    print("  All done!")
    print()
    print("  Login:  admin / admin123")
    print("  API:    http://localhost:8000/docs")
    print()


if __name__ == "__main__":
    main()
