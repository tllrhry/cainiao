"""
文章模型
- 支持草稿/已发布两种状态
- slug 用于 SEO 友好 URL
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Enum,
    ForeignKey,
    func,
)
from sqlalchemy.orm import relationship

from app.database import Base
import enum


class ArticleStatus(str, enum.Enum):
    """文章状态枚举"""
    DRAFT = "draft"          # 草稿
    PUBLISHED = "published"  # 已发布


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="文章ID")
    title = Column(String(200), nullable=False, comment="文章标题")
    slug = Column(String(200), unique=True, nullable=False, index=True, comment="URL友好标识")
    content = Column(Text, nullable=False, comment="文章内容（富文本/Markdown）")
    summary = Column(String(500), nullable=True, comment="文章摘要")
    cover_image = Column(String(500), nullable=True, comment="封面图片URL")
    status = Column(
        Enum(ArticleStatus),
        default=ArticleStatus.DRAFT,
        nullable=False,
        comment="状态：draft-草稿, published-已发布",
    )
    author_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="作者ID"
    )
    published_at = Column(DateTime, nullable=True, comment="发布时间")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关联
    author = relationship("User", lazy="selectin")

    def __repr__(self):
        return f"<Article(id={self.id}, title={self.title})>"
