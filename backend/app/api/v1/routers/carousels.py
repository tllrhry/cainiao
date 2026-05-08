"""
轮播图管理接口路由
- 前台 GET  /carousels/public  获取已启用的轮播图（无需认证）
- 后台 GET  /carousels         轮播图列表（管理员）
- 后台 POST /carousels         创建轮播图（管理员）
- 后台 PUT  /carousels/{id}    更新轮播图（管理员）
- 后台 DELETE /carousels/{id}  删除轮播图（管理员）
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.common import BaseResponse, PaginatedResponse, PaginationMeta
from app.schemas.carousel import CarouselCreate, CarouselUpdate, CarouselOut
from app.crud import carousel as crud
from app.deps.security import require_admin
from app.models.user import User

router = APIRouter(prefix="/carousels", tags=["轮播图管理"])


# ==================== 前台公开接口 ====================

@router.get(
    "/public",
    response_model=BaseResponse[list[CarouselOut]],
    summary="获取已启用的轮播图（前台）",
    description="无需认证。返回所有 is_active=True 的轮播图，按 sort_order 升序排列。",
)
def list_public_carousels(db: Session = Depends(get_db)):
    """前台轮播图列表"""
    items = crud.get_active_carousels(db)
    return BaseResponse(
        message="获取成功",
        data=[CarouselOut.model_validate(item) for item in items],
    )


# ==================== 后台管理接口 ====================

@router.get(
    "",
    response_model=PaginatedResponse[CarouselOut],
    summary="获取轮播图列表（管理端）",
    description="支持分页和按启用状态筛选。需要管理员权限。",
)
def list_carousels(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
    is_active: Optional[bool] = Query(None, description="筛选启用状态"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """轮播图列表 —— 管理员"""
    skip = (page - 1) * page_size
    items = crud.get_carousels(db, skip=skip, limit=page_size, is_active=is_active)
    total = crud.count_carousels(db, is_active=is_active)

    return PaginatedResponse(
        message="获取成功",
        data=[CarouselOut.model_validate(item) for item in items],
        meta=PaginationMeta(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=(total + page_size - 1) // page_size,
        ),
    )


@router.post(
    "",
    response_model=BaseResponse[CarouselOut],
    status_code=status.HTTP_201_CREATED,
    summary="创建轮播图",
    description="新增一条轮播图记录。需要管理员权限。",
)
def create_carousel(
    body: CarouselCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """创建轮播图"""
    item = crud.create_carousel(
        db,
        title=body.title,
        image_url=body.image_url,
        link_url=body.link_url,
        sort_order=body.sort_order,
        is_active=body.is_active,
    )
    return BaseResponse(
        message="轮播图创建成功",
        data=CarouselOut.model_validate(item),
    )


@router.put(
    "/{carousel_id}",
    response_model=BaseResponse[CarouselOut],
    summary="更新轮播图",
    description="更新轮播图字段（只传需要修改的字段即可）。需要管理员权限。",
)
def update_carousel(
    carousel_id: int,
    body: CarouselUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """更新轮播图"""
    item = crud.get_carousel(db, carousel_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"轮播图不存在（id={carousel_id}）",
        )

    item = crud.update_carousel(
        db,
        item,
        title=body.title,
        image_url=body.image_url,
        link_url=body.link_url,
        sort_order=body.sort_order,
        is_active=body.is_active,
    )
    return BaseResponse(
        message="轮播图更新成功",
        data=CarouselOut.model_validate(item),
    )


@router.delete(
    "/{carousel_id}",
    response_model=BaseResponse[None],
    summary="删除轮播图",
    description="删除一条轮播图记录。需要管理员权限。",
)
def delete_carousel(
    carousel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """删除轮播图"""
    item = crud.get_carousel(db, carousel_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"轮播图不存在（id={carousel_id}）",
        )

    crud.delete_carousel(db, item)
    return BaseResponse(message="轮播图已删除")
