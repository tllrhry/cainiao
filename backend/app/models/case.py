"""
案例模型
- cases: 案例主表，分类为：文化墙/展厅/主题公园/雕塑/小品
- case_images: 案例多图关联表
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Enum,
    ForeignKey,
    func,
)
from sqlalchemy.orm import relationship

from app.database import Base
import enum


class CaseStatus(str, enum.Enum):
    """案例状态枚举"""
    DRAFT = "draft"          # 草稿
    PUBLISHED = "published"  # 已发布


class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="案例ID")
    title = Column(String(200), nullable=False, comment="案例标题")
    description = Column(Text, nullable=True, comment="案例描述")
    category = Column(
        String(50),
        nullable=False,
        index=True,
        comment="案例分类：文化墙/展厅/主题公园/雕塑/小品",
    )
    cover_image = Column(String(500), nullable=True, comment="封面图片URL")
    status = Column(
        Enum(CaseStatus),
        default=CaseStatus.DRAFT,
        nullable=False,
        comment="状态：draft-草稿, published-已发布",
    )
    sort_order = Column(Integer, default=0, nullable=False, comment="排序序号（越小越靠前）")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关联：一个案例有多张图片
    images = relationship(
        "CaseImage", back_populates="case", cascade="all, delete-orphan", lazy="selectin"
    )

    def __repr__(self):
        return f"<Case(id={self.id}, title={self.title}, category={self.category})>"


class CaseImage(Base):
    __tablename__ = "case_images"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="图片ID")
    case_id = Column(
        Integer,
        ForeignKey("cases.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="所属案例ID",
    )
    image_url = Column(String(500), nullable=False, comment="图片URL")
    sort_order = Column(Integer, default=0, nullable=False, comment="排序序号（越小越靠前）")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    # 关联
    case = relationship("Case", back_populates="images")

    def __repr__(self):
        return f"<CaseImage(id={self.id}, case_id={self.case_id})>"
