"""
文件上传 Pydantic Schemas
"""

from typing import List

from pydantic import BaseModel, Field


class FileOut(BaseModel):
    """单文件上传响应"""
    url: str = Field(..., description="可访问的文件路径（如 /static/uploads/xxx.jpg）")
    filename: str = Field("", description="原始文件名")


class FilesOut(BaseModel):
    """多文件上传响应"""
    files: List[FileOut] = Field(..., description="成功上传的文件列表")
    count: int = Field(..., description="成功上传数量")
