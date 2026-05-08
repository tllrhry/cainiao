"""
案例 CRUD 操作
支持案例主表 + 多图关联（case_images）的联动增删改。
"""

from typing import List, Optional

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.models.case import Case, CaseImage, CaseStatus


# ==================== 案例 ====================


def get_case(db: Session, case_id: int) -> Optional[Case]:
    """按 ID 获取单个案例（含图片关联）"""
    return (
        db.query(Case)
        .options(joinedload(Case.images))
        .filter(Case.id == case_id)
        .first()
    )


def get_cases(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    status: Optional[CaseStatus] = None,
    category: Optional[str] = None,
) -> List[Case]:
    """
    获取案例列表，支持按状态和分类筛选。
    按 sort_order 升序、created_at 降序排列。
    """
    query = db.query(Case).options(joinedload(Case.images))

    if status is not None:
        query = query.filter(Case.status == status)
    if category:
        query = query.filter(Case.category == category)

    return (
        query
        .order_by(Case.sort_order.asc(), Case.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def count_cases(
    db: Session,
    status: Optional[CaseStatus] = None,
    category: Optional[str] = None,
) -> int:
    """统计案例总数"""
    query = db.query(Case)
    if status is not None:
        query = query.filter(Case.status == status)
    if category:
        query = query.filter(Case.category == category)
    return query.count()


def get_case_categories(db: Session) -> List[dict]:
    """
    获取案例分类列表（去重 + 统计数量）。
    仅统计已发布的案例。
    """
    rows = (
        db.query(Case.category, func.count(Case.id).label("count"))
        .filter(Case.status == CaseStatus.PUBLISHED)
        .group_by(Case.category)
        .order_by(Case.category)
        .all()
    )
    return [{"category": r.category, "count": r.count} for r in rows]


def create_case(
    db: Session,
    title: str,
    description: Optional[str],
    category: str,
    cover_image: Optional[str],
    status: CaseStatus,
    sort_order: int,
    images: Optional[List[dict]] = None,
) -> Case:
    """创建案例，可选附带多张图片"""
    case = Case(
        title=title,
        description=description,
        category=category,
        cover_image=cover_image,
        status=status,
        sort_order=sort_order,
    )
    db.add(case)
    db.flush()  # 获取 case.id

    # 添加关联图片
    if images:
        for img in images:
            case_image = CaseImage(
                case_id=case.id,
                image_url=img["image_url"],
                sort_order=img.get("sort_order", 0),
            )
            db.add(case_image)

    db.commit()
    db.refresh(case)
    return case


def update_case(
    db: Session,
    case: Case,
    title: Optional[str] = None,
    description: Optional[str] = None,
    category: Optional[str] = None,
    cover_image: Optional[str] = None,
    status: Optional[CaseStatus] = None,
    sort_order: Optional[int] = None,
    images: Optional[List[dict]] = None,
) -> Case:
    """
    更新案例字段。若传 images 参数则全量替换图片（先删后建）。
    """
    # 更新主表字段
    for key, value in [
        ("title", title),
        ("description", description),
        ("category", category),
        ("cover_image", cover_image),
        ("status", status),
        ("sort_order", sort_order),
    ]:
        if value is not None:
            setattr(case, key, value)

    # 全量替换图片
    if images is not None:
        # 删除旧图片
        db.query(CaseImage).filter(CaseImage.case_id == case.id).delete()
        # 添加新图片
        for img in images:
            case_image = CaseImage(
                case_id=case.id,
                image_url=img["image_url"],
                sort_order=img.get("sort_order", 0),
            )
            db.add(case_image)

    db.commit()
    db.refresh(case)
    return case


def delete_case(db: Session, case: Case) -> None:
    """删除案例（cascade 自动删除关联图片）"""
    db.delete(case)
    db.commit()
