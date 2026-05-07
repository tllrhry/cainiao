"""
公司信息模型
KV 结构存储：公司名称、简介、联系方式等前台展示内容
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, func

from app.database import Base


class CompanyInfo(Base):
    __tablename__ = "company_info"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="记录ID")
    key = Column(String(100), unique=True, nullable=False, index=True, comment="配置键（如 company_name, about_us）")
    value = Column(Text, nullable=True, comment="配置值（文本或HTML内容）")
    type = Column(
        String(20), default="text", nullable=False, comment="值类型：text-纯文本, image-图片URL, html-富文本"
    )
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    def __repr__(self):
        return f"<CompanyInfo(key={self.key})>"
