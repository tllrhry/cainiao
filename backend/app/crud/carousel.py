"""
轮播图 CRUD 操作
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.carousel import Carousel


def get_carousel(db: Session, carousel_id: int) -> Optional[Carousel]:
    """按 ID 获取单条轮播图"""
    return db.query(Carousel).filter(Carousel.id == carousel_id).first()


def get_carousels(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
) -> List[Carousel]:
    """
    获取轮播图列表，支持按启用状态筛选。
    按 sort_order 升序排列。
    """
    query = db.query(Carousel)
    if is_active is not None:
        query = query.filter(Carousel.is_active == is_active)
    return query.order_by(Carousel.sort_order.asc()).offset(skip).limit(limit).all()


def get_active_carousels(db: Session) -> List[Carousel]:
    """获取所有已启用的轮播图（前台用）"""
    return (
        db.query(Carousel)
        .filter(Carousel.is_active == True)
        .order_by(Carousel.sort_order.asc())
        .all()
    )


def count_carousels(db: Session, is_active: Optional[bool] = None) -> int:
    """统计轮播图总数（可按启用状态筛选）"""
    query = db.query(Carousel)
    if is_active is not None:
        query = query.filter(Carousel.is_active == is_active)
    return query.count()


def create_carousel(
    db: Session,
    title: Optional[str],
    image_url: str,
    link_url: Optional[str],
    sort_order: int,
    is_active: bool,
) -> Carousel:
    """创建一条轮播图记录"""
    carousel = Carousel(
        title=title,
        image_url=image_url,
        link_url=link_url,
        sort_order=sort_order,
        is_active=is_active,
    )
    db.add(carousel)
    db.commit()
    db.refresh(carousel)
    return carousel


def update_carousel(db: Session, carousel: Carousel, **kwargs) -> Carousel:
    """更新轮播图字段（仅更新非 None 的字段）"""
    for key, value in kwargs.items():
        if value is not None:
            setattr(carousel, key, value)
    db.commit()
    db.refresh(carousel)
    return carousel


def delete_carousel(db: Session, carousel: Carousel) -> None:
    """删除一条轮播图"""
    db.delete(carousel)
    db.commit()
