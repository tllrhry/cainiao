"""
轮播图 Pydantic Schemas
"""

from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field


class CarouselBase(BaseModel):
    """轮播图基础字段"""
    title: Optional[str] = Field(None, max_length=200, description="轮播图标题（alt 文本）")
    image_url: str = Field(..., max_length=500, description="图片 URL")
    link_url: Optional[str] = Field(None, max_length=500, description="点击跳转链接")
    sort_order: int = Field(0, ge=0, description="排序序号（越小越靠前）")
    is_active: bool = Field(True, description="是否启用")


class CarouselCreate(CarouselBase):
    """创建轮播图 —— 继承基础字段"""
    pass


class CarouselUpdate(BaseModel):
    """更新轮播图 —— 所有字段可选"""
    title: Optional[str] = Field(None, max_length=200, description="轮播图标题")
    image_url: Optional[str] = Field(None, max_length=500, description="图片 URL")
    link_url: Optional[str] = Field(None, max_length=500, description="点击跳转链接")
    sort_order: Optional[int] = Field(None, ge=0, description="排序序号")
    is_active: Optional[bool] = Field(None, description="是否启用")


class CarouselOut(CarouselBase):
    """轮播图响应（含自增 ID + 时间戳）"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
