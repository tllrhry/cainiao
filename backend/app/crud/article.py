"""
文章 CRUD 操作
"""

from typing import List, Optional

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_

from app.models.article import Article, ArticleStatus


def get_article(db: Session, article_id: int) -> Optional[Article]:
    """按 ID 获取单篇文章（含作者关联）"""
    return (
        db.query(Article)
        .options(joinedload(Article.author))
        .filter(Article.id == article_id)
        .first()
    )


def get_article_by_slug(db: Session, slug: str) -> Optional[Article]:
    """按 slug 获取单篇文章（含作者关联）"""
    return (
        db.query(Article)
        .options(joinedload(Article.author))
        .filter(Article.slug == slug)
        .first()
    )


def get_articles(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    status: Optional[ArticleStatus] = None,
    keyword: Optional[str] = None,
) -> List[Article]:
    """
    获取文章列表，支持按状态和关键字筛选。
    前台只取已发布，后台可取全部。
    """
    query = db.query(Article).options(joinedload(Article.author))

    if status is not None:
        query = query.filter(Article.status == status)

    if keyword:
        like_pattern = f"%{keyword}%"
        query = query.filter(
            or_(
                Article.title.ilike(like_pattern),
                Article.summary.ilike(like_pattern),
            )
        )

    return (
        query
        .order_by(Article.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def count_articles(
    db: Session,
    status: Optional[ArticleStatus] = None,
    keyword: Optional[str] = None,
) -> int:
    """统计文章总数"""
    query = db.query(Article)

    if status is not None:
        query = query.filter(Article.status == status)

    if keyword:
        like_pattern = f"%{keyword}%"
        query = query.filter(
            or_(
                Article.title.ilike(like_pattern),
                Article.summary.ilike(like_pattern),
            )
        )

    return query.count()


def create_article(
    db: Session,
    title: str,
    slug: str,
    content: str,
    summary: Optional[str],
    cover_image: Optional[str],
    status: ArticleStatus,
    author_id: int,
) -> Article:
    """创建文章。若状态为 published 则自动设置 published_at。"""
    from datetime import datetime

    article = Article(
        title=title,
        slug=slug,
        content=content,
        summary=summary,
        cover_image=cover_image,
        status=status,
        author_id=author_id,
        published_at=datetime.now() if status == ArticleStatus.PUBLISHED else None,
    )
    db.add(article)
    db.commit()
    db.refresh(article)
    return article


def update_article(db: Session, article: Article, **kwargs) -> Article:
    """更新文章字段。若状态改为 published 且之前未发布，自动设置 published_at。"""
    from datetime import datetime

    new_status = kwargs.get("status")
    if new_status == ArticleStatus.PUBLISHED and article.status != ArticleStatus.PUBLISHED:
        kwargs["published_at"] = datetime.now()

    for key, value in kwargs.items():
        if value is not None:
            setattr(article, key, value)

    db.commit()
    db.refresh(article)
    return article


def delete_article(db: Session, article: Article) -> None:
    """删除文章"""
    db.delete(article)
    db.commit()


def increment_view_count(db: Session, article: Article) -> Article:
    """递增文章阅读量"""
    article.view_count = (article.view_count or 0) + 1
    db.commit()
    db.refresh(article)
    return article
