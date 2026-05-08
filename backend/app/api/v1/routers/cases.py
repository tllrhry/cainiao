"""
案例管理接口路由

前台（无需认证）：
  GET  /cases            已发布案例列表（分页 + 分类筛选）
  GET  /cases/categories 案例分类列表（含计数）
  GET  /cases/{id}       案例详情（含所有图片）

后台（管理员）：
  GET  /cases/admin      全部案例列表（含草稿）
  POST /cases            创建案例（支持多图）
  PUT  /cases/{id}       更新案例（支持全量替换图片）
  DELETE /cases/{id}     删除案例
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.common import BaseResponse, PaginatedResponse, PaginationMeta
from app.schemas.case import (
    CaseCreate,
    CaseUpdate,
    CaseOut,
    CaseListOut,
    CaseCategoryOut,
)
from app.crud import case as crud
from app.deps.security import require_admin
from app.models.user import User
from app.models.case import CaseStatus

router = APIRouter(prefix="/cases", tags=["案例管理"])


# ==================== 前台公开接口 ====================

@router.get(
    "",
    response_model=PaginatedResponse[CaseListOut],
    summary="获取案例列表（前台）",
    description="返回已发布的案例列表，支持分页和分类筛选。无需认证。",
)
def list_cases(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(12, ge=1, le=50, description="每页条数"),
    category: Optional[str] = Query(None, description="分类筛选：品牌视觉 / 文化空间 / 主题文旅 / 商业空间 / 数字视觉 / 雕塑小品 / 活动美陈 / 广告设计"),
    db: Session = Depends(get_db),
):
    """前台案例列表"""
    skip = (page - 1) * page_size
    items = crud.get_cases(
        db,
        skip=skip,
        limit=page_size,
        status=CaseStatus.PUBLISHED,
        category=category,
    )
    total = crud.count_cases(db, status=CaseStatus.PUBLISHED, category=category)

    return PaginatedResponse(
        message="获取成功",
        data=[CaseListOut.model_validate(item) for item in items],
        meta=PaginationMeta(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=(total + page_size - 1) // page_size if total > 0 else 1,
        ),
    )


@router.get(
    "/categories",
    response_model=BaseResponse[list[CaseCategoryOut]],
    summary="获取案例分类列表",
    description="返回所有在已发布案例中出现的分类及数量。无需认证。",
)
def list_case_categories(db: Session = Depends(get_db)):
    """案例分类列表"""
    items = crud.get_case_categories(db)
    return BaseResponse(
        message="获取成功",
        data=[CaseCategoryOut(**item) for item in items],
    )


@router.get(
    "/{case_id}",
    response_model=BaseResponse[CaseOut],
    summary="获取案例详情",
    description="按 ID 获取已发布案例的完整信息（含所有图片）。无需认证。",
)
def get_case(case_id: int, db: Session = Depends(get_db)):
    """案例详情"""
    case = crud.get_case(db, case_id)
    if not case or case.status != CaseStatus.PUBLISHED:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="案例不存在或未发布",
        )
    return BaseResponse(
        message="获取成功",
        data=CaseOut.model_validate(case),
    )


# ==================== 后台管理接口 ====================

@router.get(
    "/admin/list",
    response_model=PaginatedResponse[CaseListOut],
    summary="获取案例列表（管理端）",
    description="返回全部案例（含草稿），支持分页、分类筛选和状态筛选。需要管理员权限。",
)
def list_cases_admin(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(12, ge=1, le=50, description="每页条数"),
    status: Optional[CaseStatus] = Query(None, description="状态筛选"),
    category: Optional[str] = Query(None, description="分类筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """管理端案例列表"""
    skip = (page - 1) * page_size
    items = crud.get_cases(db, skip=skip, limit=page_size, status=status, category=category)
    total = crud.count_cases(db, status=status, category=category)

    return PaginatedResponse(
        message="获取成功",
        data=[CaseListOut.model_validate(item) for item in items],
        meta=PaginationMeta(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=(total + page_size - 1) // page_size if total > 0 else 1,
        ),
    )


@router.get(
    "/admin/{case_id}",
    response_model=BaseResponse[CaseOut],
    summary="获取案例详情（管理端）",
    description="按 ID 获取案例完整信息（含所有图片，含草稿）。需要管理员权限。",
)
def get_case_admin(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """管理端案例详情"""
    case = crud.get_case(db, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="案例不存在")
    return BaseResponse(message="获取成功", data=CaseOut.model_validate(case))


@router.post(
    "",
    response_model=BaseResponse[CaseOut],
    status_code=status.HTTP_201_CREATED,
    summary="创建案例",
    description="创建案例，可附带多张图片 URL（图片需提前通过 /upload 接口上传）。需要管理员权限。",
)
def create_case(
    body: CaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """创建案例"""
    # 准备图片数据
    images = None
    if body.images:
        images = [img.model_dump() for img in body.images]

    case = crud.create_case(
        db,
        title=body.title,
        description=body.description,
        category=body.category,
        cover_image=body.cover_image,
        status=body.status,
        sort_order=body.sort_order,
        images=images,
    )
    return BaseResponse(
        message="案例创建成功",
        data=CaseOut.model_validate(case),
    )


@router.put(
    "/{case_id}",
    response_model=BaseResponse[CaseOut],
    summary="更新案例",
    description="更新案例字段。若传 images 参数，将全量替换案例图片。需要管理员权限。",
)
def update_case(
    case_id: int,
    body: CaseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """更新案例"""
    case = crud.get_case(db, case_id)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"案例不存在（id={case_id}）",
        )

    # 准备图片数据
    images = None
    if body.images is not None:
        images = [img.model_dump() for img in body.images]

    case = crud.update_case(
        db,
        case,
        title=body.title,
        description=body.description,
        category=body.category,
        cover_image=body.cover_image,
        status=body.status,
        sort_order=body.sort_order,
        images=images,
    )
    return BaseResponse(
        message="案例更新成功",
        data=CaseOut.model_validate(case),
    )


@router.delete(
    "/{case_id}",
    response_model=BaseResponse[None],
    summary="删除案例",
    description="删除案例及其所有关联图片（级联删除）。需要管理员权限。",
)
def delete_case(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """删除案例"""
    case = crud.get_case(db, case_id)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"案例不存在（id={case_id}）",
        )

    crud.delete_case(db, case)
    return BaseResponse(message="案例已删除")
