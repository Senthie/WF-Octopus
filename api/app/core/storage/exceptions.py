"""
Author: '浪川' '1214391613@qq.com'
Date: 2026-04-24 11:54:37
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-04-24 12:01:37
FilePath: /api/app/core/storage/exceptions.py
Description: 存储系统自定义异常

Copyright (c) 2026 by '浪川' email: '1214391613@qq.com', All Rights Reserved.
"""

from typing import Optional


class StorageError(Exception):
    """存储系统基础异常"""

    def __init__(self, message: str, details: Optional[dict] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class FileNotFoundError(StorageError):
    """文件不存在异常"""

    def __init__(self, file_id: str):
        super().__init__(message=f'File not found: {file_id}', details={'file_id': file_id})


class FileUploadError(StorageError):
    """文件上传失败异常"""

    def __init__(self, filename: str, reason: str):
        super().__init__(
            message=f'Failed to upload file: {filename}',
            details={'filename': filename, 'reason': reason},
        )


class FileDownloadError(StorageError):
    """文件下载失败异常"""

    def __init__(self, file_id: str, reason: str):
        super().__init__(
            message=f'Failed to download file: {file_id}',
            details={'file_id': file_id, 'reason': reason},
        )


class FileDeletionError(StorageError):
    """文件删除失败异常"""

    def __init__(self, file_id: str, reason: str):
        super().__init__(
            message=f'Failed to delete file: {file_id}',
            details={'file_id': file_id, 'reason': reason},
        )


class StorageConnectionError(StorageError):
    """存储系统连接失败异常"""

    def __init__(self, backend: str, reason: str):
        super().__init__(
            message=f'Failed to connect to storage backend: {backend}',
            details={'backend': backend, 'reason': reason},
        )
