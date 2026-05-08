"""
公司信息公开接口

前台（无需认证）：
  GET  /company-info  获取所有公司信息配置（KV 列表）
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.common import BaseResponse
from app.schemas.company import CompanyInfoOut
from app.crud import company as crud

router = APIRouter(prefix="/company-info", tags=["公司信息"])


@router.get(
    "",
    response_model=BaseResponse[list[CompanyInfoOut]],
    summary="获取公司信息",
    description="返回所有公司信息配置项（KV 结构），用于前台首页展示。无需认证。",
)
def get_company_info(db: Session = Depends(get_db)):
    """获取公司信息"""
    items = crud.get_all(db)
    return BaseResponse(
        message="获取成功",
        data=[CompanyInfoOut.model_validate(item) for item in items],
    )
