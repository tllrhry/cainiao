"""
文件上传接口路由
- POST /upload/single    单图上传
- POST /upload/multiple  多图上传（最多 9 张）
"""

from fastapi import APIRouter, Depends, UploadFile, File

from app.schemas.common import BaseResponse
from app.schemas.file import FileOut, FilesOut
from app.utils.upload import validate_image, save_upload
from app.deps.security import require_admin

router = APIRouter(prefix="/upload", tags=["文件上传"])


@router.post(
    "/single",
    response_model=BaseResponse[FileOut],
    summary="单张图片上传",
    description="上传一张图片（支持 jpg/jpeg/png/gif/webp），返回可访问路径。需要管理员权限。",
)
async def upload_single(
    file: UploadFile = File(..., description="上传的图片文件"),
    _admin=Depends(require_admin),
):
    """单图上传"""
    ext = validate_image(file)
    url = save_upload(file, ext)
    return BaseResponse(
        message="上传成功",
        data=FileOut(url=url, filename=file.filename or ""),
    )


@router.post(
    "/multiple",
    response_model=BaseResponse[FilesOut],
    summary="多张图片上传",
    description="一次上传多张图片（建议不超过 9 张），返回所有文件的访问路径。需要管理员权限。",
)
async def upload_multiple(
    files: list[UploadFile] = File(..., description="上传的图片文件列表"),
    _admin=Depends(require_admin),
):
    """多图上传"""
    uploaded: list[FileOut] = []
    for file in files:
        ext = validate_image(file)
        url = save_upload(file, ext)
        uploaded.append(FileOut(url=url, filename=file.filename or ""))

    return BaseResponse(
        message=f"成功上传 {len(uploaded)} 个文件",
        data=FilesOut(files=uploaded, count=len(uploaded)),
    )
