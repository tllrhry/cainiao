"""
文件上传工具函数
支持单图 / 多图上传，含格式校验、大小校验、自动重命名。
"""

import os
import uuid
from typing import List

from fastapi import UploadFile, HTTPException, status

from app.config import settings

# 允许的图片扩展名
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp"}

# 允许的 MIME 类型
ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
}


def _get_uploads_dir() -> str:
    """获取 uploads 目录的绝对路径（backend/static/uploads/）"""
    # __file__ 位于 backend/app/utils/upload.py
    # 向上 3 级到达 backend/
    backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    upload_dir = os.path.join(backend_dir, settings.UPLOAD_DIR)
    os.makedirs(upload_dir, exist_ok=True)
    return upload_dir


def validate_image(file: UploadFile) -> str:
    """
    校验图片文件：格式、MIME 类型、文件大小。
    校验通过返回小写扩展名（不含点）。
    """
    # 1. 文件名不能为空
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件名不能为空",
        )

    # 2. 校验扩展名
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if not ext or ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的图片格式「.{ext}」，仅支持：{', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    # 3. 校验 MIME 类型（content_type 可能为空，容错处理）
    if file.content_type and file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的 MIME 类型「{file.content_type}」",
        )

    return ext


def generate_filename(ext: str) -> str:
    """生成唯一文件名：UUID hex + 扩展名"""
    return f"{uuid.uuid4().hex}.{ext}"


def save_upload(file: UploadFile, ext: str) -> str:
    """
    将上传文件保存到磁盘，返回前端可访问的相对 URL 路径。
    写入磁盘后会检查实际文件大小是否超限。
    """
    filename = generate_filename(ext)
    upload_dir = _get_uploads_dir()
    file_path = os.path.join(upload_dir, filename)

    # 读取全部内容（MAX_UPLOAD_SIZE = 10MB，内存可承受）
    content = file.file.read()

    # 大小校验
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"文件大小超过限制（最大 {settings.MAX_UPLOAD_SIZE // (1024 * 1024)}MB），"
                   f"当前文件 {len(content) / (1024 * 1024):.1f}MB",
        )

    # 写入磁盘
    with open(file_path, "wb") as f:
        f.write(content)

    # 返回前端可访问路径，例如 /static/uploads/abc123.jpg
    return f"/{settings.UPLOAD_DIR}/{filename}"
