"""
公司信息 Pydantic Schemas
"""

from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field


class CompanyInfoOut(BaseModel):
    """单条公司信息响应"""
    key: str = Field(..., description="配置键")
    value: Optional[str] = Field(None, description="配置值")
    type: str = Field("text", description="值类型：text / image / html")
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
