"""
轮播图模型
首页大轮播图管理
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, func

from app.database import Base


class Carousel(Base):
    __tablename__ = "carousels"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="轮播图ID")
    title = Column(String(200), nullable=True, comment="轮播图标题（alt文本）")
    image_url = Column(String(500), nullable=False, comment="图片URL")
    link_url = Column(String(500), nullable=True, comment="点击跳转链接")
    sort_order = Column(Integer, default=0, nullable=False, comment="排序序号（越小越靠前）")
    is_active = Column(Boolean, default=True, nullable=False, comment="是否启用")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    def __repr__(self):
        return f"<Carousel(id={self.id}, title={self.title})>"
