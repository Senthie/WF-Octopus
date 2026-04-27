"""
Author: '浪川' '1214391613@qq.com'
Date: 2026-04-07 11:36:36
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-04-23 16:22:05
FilePath: /api/app/apis/v1/file.py
Description: get files api point

Copyright (c) 2026 by '浪川' email: '1214391613@qq.com', All Rights Reserved.
"""

from pathlib import Path

from fastapi import APIRouter, HTTPException, Path as PathParam
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

router = APIRouter(prefix='/file', tags=['file v1'])

# 基础目录（建议使用绝对路径，可从配置读取）
TMP_BASE = Path('app/tmp')
TMP_BASE = TMP_BASE.resolve()  # 转为绝对路径


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
