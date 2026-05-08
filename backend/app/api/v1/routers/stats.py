"""
仪表盘统计接口路由
- GET /stats 返回文章数、案例数、轮播图数（管理员）
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.common import BaseResponse
from app.deps.security import require_admin
from app.models.user import User
from app.models.article import Article
from app.models.case import Case
from app.models.carousel import Carousel

router = APIRouter(prefix="/stats", tags=["仪表盘"])


@router.get(
    "",
    response_model=BaseResponse[dict],
    summary="获取仪表盘统计数据",
    description="返回文章数、案例数、轮播图数。需要管理员权限。",
)
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """仪表盘统计"""
    articles_count = db.query(Article).count()
    cases_count = db.query(Case).count()
    carousels_count = db.query(Carousel).count()

    return BaseResponse(
        message="获取成功",
        data={
            "articles": articles_count,
            "cases": cases_count,
            "carousels": carousels_count,
        },
    )
