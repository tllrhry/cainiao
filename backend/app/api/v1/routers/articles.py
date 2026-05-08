"""
文章管理接口路由

前台（无需认证）：
  GET  /articles             已发布文章列表（分页 + 搜索）
  GET  /articles/{slug}      文章详情

后台（管理员）：
  GET  /articles/admin       全部文章列表（含草稿筛选）
  POST /articles             创建文章
  PUT  /articles/{id}        更新文章
  DELETE /articles/{id}      删除文章
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.common import BaseResponse, PaginatedResponse, PaginationMeta
from app.schemas.article import (
    ArticleCreate,
    ArticleUpdate,
    ArticleOut,
    ArticleListOut,
)
from app.crud import article as crud
from app.deps.security import get_current_user, require_admin
from app.models.user import User
from app.models.article import ArticleStatus

router = APIRouter(prefix="/articles", tags=["文章管理"])


# ==================== 前台公开接口 ====================

@router.get(
    "",
    response_model=PaginatedResponse[ArticleListOut],
    summary="获取文章列表（前台）",
    description="返回已发布的文章列表，支持分页和关键字搜索。无需认证。",
)
def list_articles(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=50, description="每页条数"),
    keyword: Optional[str] = Query(None, description="搜索关键字（标题 / 摘要）"),
    db: Session = Depends(get_db),
):
    """前台文章列表 —— 仅返回已发布文章"""
    skip = (page - 1) * page_size
    items = crud.get_articles(
        db,
        skip=skip,
        limit=page_size,
        status=ArticleStatus.PUBLISHED,
        keyword=keyword,
    )
    total = crud.count_articles(db, status=ArticleStatus.PUBLISHED, keyword=keyword)

    return PaginatedResponse(
        message="获取成功",
        data=[ArticleListOut.model_validate(item) for item in items],
        meta=PaginationMeta(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=(total + page_size - 1) // page_size,
        ),
    )


@router.get(
    "/{slug}",
    response_model=BaseResponse[ArticleOut],
    summary="获取文章详情",
    description="按 slug 获取已发布文章的完整内容。无需认证。",
)
def get_article(slug: str, db: Session = Depends(get_db)):
    """文章详情"""
    article = crud.get_article_by_slug(db, slug)
    if not article or article.status != ArticleStatus.PUBLISHED:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文章不存在或未发布",
        )
    return BaseResponse(
        message="获取成功",
        data=ArticleOut.model_validate(article),
    )


@router.post(
    "/{slug}/view",
    response_model=BaseResponse[ArticleOut],
    summary="递增阅读量",
    description="文章每被阅读一次，调用此接口 +1。无需认证。",
)
def increment_view(slug: str, db: Session = Depends(get_db)):
    """递增文章阅读量"""
    article = crud.get_article_by_slug(db, slug)
    if not article or article.status != ArticleStatus.PUBLISHED:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文章不存在或未发布",
        )
    article = crud.increment_view_count(db, article)
    return BaseResponse(
        message="阅读量 +1",
        data=ArticleOut.model_validate(article),
    )


# ==================== 后台管理接口 ====================

@router.get(
    "/admin/list",
    response_model=PaginatedResponse[ArticleListOut],
    summary="获取文章列表（管理端）",
    description="返回全部文章（含草稿），支持分页、状态筛选和关键字搜索。需要管理员权限。",
)
def list_articles_admin(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=50, description="每页条数"),
    status: Optional[ArticleStatus] = Query(None, description="状态筛选：draft / published"),
    keyword: Optional[str] = Query(None, description="搜索关键字"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """管理端文章列表"""
    skip = (page - 1) * page_size
    items = crud.get_articles(db, skip=skip, limit=page_size, status=status, keyword=keyword)
    total = crud.count_articles(db, status=status, keyword=keyword)

    return PaginatedResponse(
        message="获取成功",
        data=[ArticleListOut.model_validate(item) for item in items],
        meta=PaginationMeta(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=(total + page_size - 1) // page_size,
        ),
    )


@router.get(
    "/admin/{article_id}",
    response_model=BaseResponse[ArticleOut],
    summary="获取文章详情（管理端）",
    description="按 ID 获取文章完整内容（含草稿）。需要管理员权限。",
)
def get_article_admin(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """管理端文章详情"""
    article = crud.get_article(db, article_id)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"文章不存在（id={article_id}）",
        )
    return BaseResponse(
        message="获取成功",
        data=ArticleOut.model_validate(article),
    )


@router.post(
    "",
    response_model=BaseResponse[ArticleOut],
    status_code=status.HTTP_201_CREATED,
    summary="创建文章",
    description="创建一篇文章（默认草稿，可直接发布）。需要管理员权限。",
)
def create_article(
    body: ArticleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """创建文章"""
    # slug 唯一性校验
    existing = crud.get_article_by_slug(db, body.slug)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"slug「{body.slug}」已被使用，请换一个",
        )

    article = crud.create_article(
        db,
        title=body.title,
        slug=body.slug,
        content=body.content,
        summary=body.summary,
        cover_image=body.cover_image,
        status=body.status,
        author_id=current_user.id,
    )
    return BaseResponse(
        message="文章创建成功",
        data=ArticleOut.model_validate(article),
    )


@router.put(
    "/{article_id}",
    response_model=BaseResponse[ArticleOut],
    summary="更新文章",
    description="更新文章字段（只传需要修改的字段即可）。需要管理员权限。",
)
def update_article(
    article_id: int,
    body: ArticleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """更新文章"""
    article = crud.get_article(db, article_id)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"文章不存在（id={article_id}）",
        )

    # slug 唯一性校验（如果修改了 slug）
    if body.slug and body.slug != article.slug:
        existing = crud.get_article_by_slug(db, body.slug)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"slug「{body.slug}」已被使用",
            )

    article = crud.update_article(
        db,
        article,
        title=body.title,
        slug=body.slug,
        content=body.content,
        summary=body.summary,
        cover_image=body.cover_image,
        status=body.status,
    )
    return BaseResponse(
        message="文章更新成功",
        data=ArticleOut.model_validate(article),
    )


@router.delete(
    "/{article_id}",
    response_model=BaseResponse[None],
    summary="删除文章",
    description="删除一篇文章。需要管理员权限。",
)
def delete_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """删除文章"""
    article = crud.get_article(db, article_id)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"文章不存在（id={article_id}）",
        )

    crud.delete_article(db, article)
    return BaseResponse(message="文章已删除")
