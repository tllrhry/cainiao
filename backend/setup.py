"""
一键初始化脚本
- 创建数据库
- 安装 Python 依赖
- 执行 Alembic 迁移
- 创建默认管理员账号

用法：python setup.py
"""

import subprocess
import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))


def run(cmd: str, description: str = ""):
    """运行命令并打印输出"""
    if description:
        print(f"\n{'='*50}")
        print(f"  {description}")
        print(f"{'='*50}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    if result.returncode != 0:
        print(f"❌ 执行失败: {cmd}")
        sys.exit(1)
    print("✅ 完成")


def main():
    print("""
╔══════════════════════════════════════════╗
║      🐦 菜鸟设计 - 项目初始化脚本        ║
╚══════════════════════════════════════════╝
    """)

    # 1. 创建数据库
    run(
        f'mysql -u root -p"Cainiao@123" -h localhost -e "CREATE DATABASE IF NOT EXISTS cainiao_design CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"',
        "1/3 创建数据库 cainiao_design",
    )

    # 2. 安装依赖
    run(
        f"{sys.executable} -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple",
        "2/3 安装 Python 依赖",
    )

    # 3. 执行数据库迁移
    run(
        f"{sys.executable} -m alembic upgrade head",
        "3/3 执行数据库迁移（创建所有表 + 初始数据）",
    )

    print("""
╔══════════════════════════════════════════╗
║   🎉 初始化完成！                        ║
║                                          ║
║   启动后端：uvicorn app.main:app         ║
║             --reload --port 8000         ║
║                                          ║
║   下一步：创建管理员账号                   ║
║   python seed_admin.py                   ║
╚══════════════════════════════════════════╝
    """)


if __name__ == "__main__":
    main()
