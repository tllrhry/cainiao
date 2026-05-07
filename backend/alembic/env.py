"""
Alembic 环境配置
自动从 SQLAlchemy Base 元数据读取所有模型，生成迁移脚本
"""

import sys
from pathlib import Path

# 将 backend 目录加入 Python 路径，确保 `app` 模块可导入
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

from app.database import Base
from app.config import settings
import app.models  # noqa: F401 - 导入所有模型，确保 Base.metadata 包含全部表

# Alembic Config 对象
config = context.config

# 将数据库 URL 设置到 alembic 配置中
config.set_main_option("sqlalchemy.url", settings.database_url)

# 配置日志
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# MetaData 对象（包含所有模型表结构）
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    离线模式：生成 SQL 脚本而不连接数据库
    用于生产环境 DBA 审核后执行
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    在线模式：直接连接数据库执行 DDL
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
