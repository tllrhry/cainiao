"""
统一响应格式
所有接口使用 BaseResponse 包裹返回数据，保持前端解析一致性。
"""

from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    """统一 API 响应体"""

    code: int = 200
    message: str = "操作成功"
    data: Optional[T] = None

    class Config:
        json_schema_extra = {
            "example": {
                "code": 200,
                "message": "操作成功",
                "data": None,
            }
        }


class PaginationMeta(BaseModel):
    """分页元数据"""

    page: int
    page_size: int
    total: int
    total_pages: int


class PaginatedResponse(BaseResponse[T], Generic[T]):
    """分页响应 —— data 为列表，meta 携带分页信息"""

    meta: Optional[PaginationMeta] = None
