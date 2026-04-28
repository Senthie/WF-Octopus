"""
Author: '浪川' '1214391613@qq.com'
Date: 2026-04-07 11:36:36
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-04-28 17:40:58
FilePath: /api/app/apis/v1/file.py
Description: get files api point

Copyright (c) 2026 by '浪川' email: '1214391613@qq.com', All Rights Reserved.
"""

from pathlib import Path
from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Path as PathParam,
    UploadFile,
)
from fastapi.responses import FileResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.background import BackgroundTask

from app.core.logging import get_logger
from app.core.pg_database import get_session
from app.core.response import ResponseModel, response_base
from app.enums.response_code_enum import CustomResponseCodeEnum
from app.middlewares.auth import get_current_user
from app.models.auth.user import UserModel
from app.schemas import FileReferenceOut
from app.services.file_service import FileService

router = APIRouter(prefix='/file', tags=['file v1'])
logger = get_logger(__name__)

# 基础目录（建议使用绝对路径，可从配置读取）
TMP_BASE = Path('app/tmp')
TMP_BASE = TMP_BASE.resolve()  # 转为绝对路径

# 依赖注入定义
DbSession = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[UserModel, Depends(get_current_user)]


def get_organization_service(session: DbSession) -> FileService:
    """获取企业服务实例"""
    return FileService(session)


FileServiceDep = Annotated[FileService, Depends(get_organization_service)]


def is_safe_path(user_path: str, base_dir: Path) -> bool:
    """防止路径遍历攻击"""
    # 合并用户路径到基础目录
    resolved = (base_dir / user_path).resolve()
    # 检查解析后的路径是否仍在 base_dir 内
    return resolved.is_relative_to(base_dir)


@router.get('/tmp-files/{filepath:path}')
async def get_tmp_file(
    filepath: str = PathParam(..., description="文件相对路径，支持子目录，如 'subdir/photo.jpg'"),
    download: bool = False,
):
    """
    访问 app.tmp 目录下的文件
    - `download=true` 强制下载，否则浏览器内联预览（图片、PDF等）
    """
    # 1. 路径安全校验
    if not is_safe_path(filepath, TMP_BASE):
        raise HTTPException(status_code=403, detail='Forbidden: path traversal detected')
    # 2. 构建真实文件路径
    full_path = TMP_BASE / filepath

    # 3. 检查文件是否存在且为文件（不是目录）
    if not full_path.is_file():
        raise HTTPException(status_code=404, detail='File not found')
    # 4. 返回文件
    # FileResponse 会自动处理：
    #   - 流式传输（适合大文件）
    #   - 设置正确的 Content-Type（基于文件扩展名）
    #   - 支持 Range 请求（断点续传）
    #   - 背景清理任务（可选）
    filename = full_path.name
    if download:
        # 强制下载
        headers = {'Content-Disposition': f'attachment; filename={filename}'}
        return FileResponse(
            path=full_path,
            headers=headers,
            background=BackgroundTask(lambda: None),  # 可添加清理逻辑
        )
    else:
        # 内联预览（浏览器自动处理）
        return FileResponse(path=full_path)


@router.post(
    '/upload',
    summary='上传文件',
    description='上传文件到系统，自动选择存储方式（小文件用 MongoDB，大文件用 GridFS）',
)
async def upload_file(
    file: Annotated[UploadFile, File(description='要上传的文件')],
    file_service: FileServiceDep,
    user: CurrentUser,
) -> ResponseModel:
    """上传文件

    Args:
        file: 上传的文件对象
        workspace_id: 工作空间 ID（租户隔离）
        uploaded_by: 上传者用户 ID
        file_service: 文件服务实例

    Returns:
        FileUploadResponse: 文件上传响应

    Raises:
        HTTPException: 上传失败时抛出 500 错误
    """
    try:
        file_reference = await file_service.upload_file(file=file, user=user)

        return response_base.success(
            res=CustomResponseCodeEnum.SUCCESS, data=FileReferenceOut.model_validate(file_reference)
        )

    except Exception as e:
        logger.error('File upload failed', error=str(e))
        return response_base.fail(
            res=CustomResponseCodeEnum.INTERNAL_SERVER_ERROR,
            data=f'Failed to upload file: {str(e)}',
        )


@router.delete('/{id}', summary='删除检测要求')
async def delete_by_id(id: UUID, service: FileServiceDep) -> ResponseModel:
    try:
        res = await service.delete_by_id(id)
        return response_base.success(
            res=CustomResponseCodeEnum.SUCCESS,
            data=res,
        )

    except Exception as e:
        return response_base.fail(
            res=CustomResponseCodeEnum.INTERNAL_SERVER_ERROR,
            data=f'Failed to extract archive: {str(e)}',
        )
