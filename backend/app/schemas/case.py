"""
案例管理 Pydantic Schemas
"""

from typing import Optional, List
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.case import CaseStatus


# ---------- 案例图片 ----------


class CaseImageCreate(BaseModel):
    """案例图片创建输入"""
    image_url: str = Field(..., max_length=500, description="图片 URL")
    sort_order: int = Field(0, ge=0, description="排序序号")


class CaseImageOut(BaseModel):
    """案例图片响应"""
    id: int
    image_url: str
    sort_order: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ---------- 案例 ----------


class CaseBase(BaseModel):
    """案例基础字段"""
    title: str = Field(..., min_length=1, max_length=200, description="案例标题")
    description: Optional[str] = Field(None, description="案例描述")
    category: str = Field(
        ..., max_length=50, description="案例分类：品牌视觉 / 文化空间 / 主题文旅 / 商业空间 / 数字视觉 / 雕塑小品 / 活动美陈 / 广告设计"
    )
    cover_image: Optional[str] = Field(None, max_length=500, description="封面图片 URL")
    status: CaseStatus = Field(CaseStatus.DRAFT, description="状态：draft / published")
    sort_order: int = Field(0, ge=0, description="排序序号（越小越靠前）")


class CaseCreate(CaseBase):
    """创建案例 —— 可附带多张图片 URL"""
    images: Optional[List[CaseImageCreate]] = Field(None, description="案例图片列表")


class CaseUpdate(BaseModel):
    """更新案例 —— 所有字段可选。传 images 将全量替换图片。"""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="案例标题")
    description: Optional[str] = Field(None, description="案例描述")
    category: Optional[str] = Field(None, max_length=50, description="案例分类")
    cover_image: Optional[str] = Field(None, max_length=500, description="封面图片 URL")
    status: Optional[CaseStatus] = Field(None, description="状态")
    sort_order: Optional[int] = Field(None, ge=0, description="排序序号")
    images: Optional[List[CaseImageCreate]] = Field(None, description="案例图片列表（全量替换）")


class CaseOut(CaseBase):
    """案例详情响应（含图片列表）"""
    id: int
    images: List[CaseImageOut] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CaseListOut(BaseModel):
    """案例列表响应（精简字段，不含正文和全部图片）"""
    id: int
    title: str
    category: str
    cover_image: Optional[str] = None
    description: Optional[str] = None
    status: CaseStatus
    sort_order: int
    created_at: datetime

    class Config:
        from_attributes = True


class CaseCategoryOut(BaseModel):
    """案例分类统计"""
    category: str = Field(..., description="分类名称")
    count: int = Field(..., description="该分类下的案例数量")
