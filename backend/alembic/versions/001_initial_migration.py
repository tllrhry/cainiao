"""初始数据库迁移：创建所有表

创建全部 7 张表：
- users: 后台用户
- roles: 角色
- user_role: 用户-角色关联
- articles: 文章
- cases: 案例
- case_images: 案例图片
- carousels: 轮播图
- company_info: 公司信息

Revision ID: 001_initial
Create Date: 2026-05-07
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers
revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """创建所有初始表"""

    # ---------- 用户表 ----------
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="用户ID"),
        sa.Column("username", sa.String(50), nullable=False, comment="登录用户名"),
        sa.Column("password_hash", sa.String(255), nullable=False, comment="密码哈希（bcrypt）"),
        sa.Column("nickname", sa.String(50), nullable=True, comment="显示昵称"),
        sa.Column("avatar", sa.String(500), nullable=True, comment="头像URL"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1"), comment="是否启用"),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), comment="创建时间"
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
            comment="更新时间",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_comment="后台用户表",
    )
    op.create_index("ix_users_username", "users", ["username"])

    # ---------- 角色表 ----------
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="角色ID"),
        sa.Column("name", sa.String(50), nullable=False, comment="角色名称（如 admin, editor）"),
        sa.Column("description", sa.String(200), nullable=True, comment="角色描述"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_comment="角色表",
    )

    # ---------- 用户-角色关联表 ----------
    op.create_table(
        "user_role",
        sa.Column("user_id", sa.Integer(), nullable=False, comment="用户ID"),
        sa.Column("role_id", sa.Integer(), nullable=False, comment="角色ID"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "role_id"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_comment="用户-角色关联表",
    )

    # ---------- 文章表 ----------
    op.create_table(
        "articles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="文章ID"),
        sa.Column("title", sa.String(200), nullable=False, comment="文章标题"),
        sa.Column("slug", sa.String(200), nullable=False, comment="URL友好标识"),
        sa.Column("content", sa.Text(), nullable=False, comment="文章内容（富文本/Markdown）"),
        sa.Column("summary", sa.String(500), nullable=True, comment="文章摘要"),
        sa.Column("cover_image", sa.String(500), nullable=True, comment="封面图片URL"),
        sa.Column(
            "status",
            sa.Enum("draft", "published", name="articlestatus"),
            nullable=False,
            server_default="draft",
            comment="状态：draft-草稿, published-已发布",
        ),
        sa.Column("author_id", sa.Integer(), nullable=True, comment="作者ID"),
        sa.Column("published_at", sa.DateTime(), nullable=True, comment="发布时间"),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), comment="创建时间"
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
            comment="更新时间",
        ),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_comment="文章表",
    )
    op.create_index("ix_articles_slug", "articles", ["slug"])

    # ---------- 案例主表 ----------
    op.create_table(
        "cases",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="案例ID"),
        sa.Column("title", sa.String(200), nullable=False, comment="案例标题"),
        sa.Column("description", sa.Text(), nullable=True, comment="案例描述"),
        sa.Column(
            "category",
            sa.String(50),
            nullable=False,
            comment="案例分类：文化墙/展厅/主题公园/雕塑/小品",
        ),
        sa.Column("cover_image", sa.String(500), nullable=True, comment="封面图片URL"),
        sa.Column(
            "status",
            sa.Enum("draft", "published", name="casestatus"),
            nullable=False,
            server_default="draft",
            comment="状态：draft-草稿, published-已发布",
        ),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0", comment="排序序号（越小越靠前）"),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), comment="创建时间"
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
            comment="更新时间",
        ),
        sa.PrimaryKeyConstraint("id"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_comment="案例表",
    )
    op.create_index("ix_cases_category", "cases", ["category"])

    # ---------- 案例图片表 ----------
    op.create_table(
        "case_images",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="图片ID"),
        sa.Column("case_id", sa.Integer(), nullable=False, comment="所属案例ID"),
        sa.Column("image_url", sa.String(500), nullable=False, comment="图片URL"),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0", comment="排序序号（越小越靠前）"),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), comment="创建时间"
        ),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_comment="案例图片表",
    )
    op.create_index("ix_case_images_case_id", "case_images", ["case_id"])

    # ---------- 轮播图表 ----------
    op.create_table(
        "carousels",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="轮播图ID"),
        sa.Column("title", sa.String(200), nullable=True, comment="轮播图标题（alt文本）"),
        sa.Column("image_url", sa.String(500), nullable=False, comment="图片URL"),
        sa.Column("link_url", sa.String(500), nullable=True, comment="点击跳转链接"),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0", comment="排序序号（越小越靠前）"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1"), comment="是否启用"),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), comment="创建时间"
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
            comment="更新时间",
        ),
        sa.PrimaryKeyConstraint("id"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_comment="首页轮播图表",
    )

    # ---------- 公司信息表 ----------
    op.create_table(
        "company_info",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="记录ID"),
        sa.Column("key", sa.String(100), nullable=False, comment="配置键（如 company_name, about_us）"),
        sa.Column("value", sa.Text(), nullable=True, comment="配置值（文本或HTML内容）"),
        sa.Column(
            "type",
            sa.String(20),
            nullable=False,
            server_default="text",
            comment="值类型：text-纯文本, image-图片URL, html-富文本",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
            comment="更新时间",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_comment="公司信息表（KV结构）",
    )
    op.create_index("ix_company_info_key", "company_info", ["key"])

    # ---------- 插入初始数据 ----------
    # 创建管理员角色
    op.execute(
        "INSERT INTO roles (name, description) VALUES ('admin', '系统管理员，拥有全部权限')"
    )


def downgrade() -> None:
    """删除所有表"""
    op.drop_table("company_info")
    op.drop_table("carousels")
    op.drop_index("ix_case_images_case_id", table_name="case_images")
    op.drop_table("case_images")
    op.drop_index("ix_cases_category", table_name="cases")
    op.drop_table("cases")
    op.drop_index("ix_articles_slug", table_name="articles")
    op.drop_table("articles")
    op.drop_table("user_role")
    op.drop_table("roles")
    op.drop_index("ix_users_username", table_name="users")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS articlestatus")
    op.execute("DROP TYPE IF EXISTS casestatus")
