"""
文章管理 Pydantic Schemas
"""

from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.article import ArticleStatus


class ArticleBase(BaseModel):
    """文章基础字段"""
    title: str = Field(..., min_length=1, max_length=200, description="文章标题")
    slug: str = Field(..., min_length=1, max_length=200, description="URL 友好标识（唯一）")
    content: str = Field(..., min_length=1, description="文章正文（富文本 / Markdown）")
    summary: Optional[str] = Field(None, max_length=500, description="文章摘要")
    cover_image: Optional[str] = Field(None, max_length=500, description="封面图片 URL")
    status: ArticleStatus = Field(ArticleStatus.DRAFT, description="状态：draft / published")


class ArticleCreate(ArticleBase):
    """创建文章 —— 继承基础字段"""
    pass


class ArticleUpdate(BaseModel):
    """更新文章 —— 所有字段可选"""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="文章标题")
    slug: Optional[str] = Field(None, min_length=1, max_length=200, description="URL 友好标识")
    content: Optional[str] = Field(None, min_length=1, description="文章正文")
    summary: Optional[str] = Field(None, max_length=500, description="文章摘要")
    cover_image: Optional[str] = Field(None, max_length=500, description="封面图片 URL")
    status: Optional[ArticleStatus] = Field(None, description="状态：draft / published")


class AuthorInfo(BaseModel):
    """作者简要信息（嵌入在文章响应中）"""
    id: int
    username: str
    nickname: Optional[str] = None

    class Config:
        from_attributes = True


class ArticleOut(ArticleBase):
    """文章详情响应"""
    id: int
    author_id: Optional[int] = None
    author: Optional[AuthorInfo] = None
    view_count: int = 0
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ArticleListOut(BaseModel):
    """文章列表响应（精简字段，不包含正文）"""
    id: int
    title: str
    slug: str
    summary: Optional[str] = None
    cover_image: Optional[str] = None
    status: ArticleStatus
    view_count: int = 0
    author: Optional[AuthorInfo] = None
    published_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
