"""
Author: '浪川' '1214391613@qq.com'
Date: 2026-04-23 16:28:28
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-05-12 15:45:58
FilePath: /api/app/core/storage/gridfs.py
Description: MongoDB GridFS 存储后端实现

使用 MongoDB GridFS 存储大文件（>= 16MB）和小文件（< 16MB）。
GridFS 自动将大文件分块存储，支持流式读写。

Copyright (c) 2026 by '浪川' email: '1214391613@qq.com', All Rights Reserved.
"""

import hashlib
from typing import Any, AsyncGenerator, Optional
from uuid import UUID, uuid4

from fastapi import UploadFile
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from pymongo.errors import PyMongoError

from app.core.logging import get_logger
from app.core.mongodb import mongodb_client
from app.core.storage.base import StorageBackend
from app.core.storage.exceptions import (
    FileDeletionError,
    FileDownloadError,
    FileNotFoundError,
    FileUploadError,
    StorageConnectionError,
)
from app.enums.gridfs_bucket_name_enum import GridfsBucketNameEnum
from app.utils.timezone_help import tz_helper

logger = get_logger(__name__)


class GridFSBackend(StorageBackend):
    """MongoDB GridFS 存储后端"""

    def __init__(self, bucket_name: GridfsBucketNameEnum):
        self._bucket_name = bucket_name
        self._bucket: Optional[AsyncIOMotorGridFSBucket] = None

    async def _get_bucket(self) -> AsyncIOMotorGridFSBucket:
        """获取 GridFS bucket 实例（懒加载）"""
        if self._bucket is None:
            if mongodb_client.client is None:
                raise StorageConnectionError(
                    backend='GridFS', reason='MongoDB client is not connected'
                )
            db = mongodb_client.client[mongodb_client.db_name]
            self._bucket = AsyncIOMotorGridFSBucket(db, bucket_name=self._bucket_name.value)
        return self._bucket

    async def _get_files_collection(self):
        """获取 GridFS 底层的 files 集合（用于元数据操作）"""
        db = mongodb_client.client[mongodb_client.db_name]
        collection_name = f'{self._bucket_name.value}.files'
        return db[collection_name]

    async def upload(
        self,
        file: UploadFile,
        metadata: Optional[dict[str, Any]] = None,
    ) -> UUID:
        """上传文件到 GridFS（自动计算 MD5 并存储为顶级字段）"""
        bucket = await self._get_bucket()
        upload_stream = None
        try:
            await file.seek(0)
            file_uuid = uuid4()

            # 准备元数据（仅用于存储额外信息，不包含 md5 和 contentType）
            extra_metadata = metadata or {}
            # 注意：不要将 md5 和 contentType 放入 metadata，因为我们会放在顶级字段
            if 'md5' in extra_metadata:
                # 如果用户自己传了 md5，我们仍然可以将其作为顶级字段，但要求用户提供
                user_provided_md5 = extra_metadata.pop('md5')
            else:
                user_provided_md5 = None

            # 构建传给 GridFS 的 metadata（只存用户额外数据）
            gridfs_metadata = {
                'filename': file.filename,
                'upload_date': tz_helper.get_current_time(),
                **extra_metadata,  # 用户自定义的其他元数据
            }

            # 上传流
            upload_stream = bucket.open_upload_stream_with_id(
                file_id=str(file_uuid),
                filename=file.filename or 'unknown',
                metadata=gridfs_metadata,
            )

            # 分块写入并计算 MD5
            chunk_size = 1024 * 1024  # 1MB
            md5_hash = hashlib.md5() if not user_provided_md5 else None
            while True:
                chunk = await file.read(chunk_size)
                if not chunk:
                    break
                if md5_hash:
                    md5_hash.update(chunk)
                await upload_stream.write(chunk)

            # 完成上传
            await upload_stream.close()

            # 准备要更新的顶级字段
            update_fields = {}
            if user_provided_md5:
                update_fields['md5'] = user_provided_md5
                md5_hex = user_provided_md5
            else:
                md5_hex = md5_hash.hexdigest()
                update_fields['md5'] = md5_hex

            # 设置顶级 contentType
            if file.content_type:
                update_fields['contentType'] = file.content_type

            # 如果有需要更新的顶级字段，执行更新
            if update_fields:
                files_collection = await self._get_files_collection()
                await files_collection.update_one({'_id': str(file_uuid)}, {'$set': update_fields})

            logger.info(
                'File uploaded to GridFS',
                file_id=str(file_uuid),
                filename=file.filename,
                size=file.size,
                bucket=self._bucket_name.value,
                md5=md5_hex,
                content_type=file.content_type,
            )

            return file_uuid

        except PyMongoError as e:
            if upload_stream is not None:
                try:
                    await upload_stream.abort()
                except Exception:
                    pass
            logger.error(
                'MongoDB error during upload',
                filename=file.filename,
                bucket=self._bucket_name.value,
                error=str(e),
            )
            raise FileUploadError(filename=file.filename or 'unknown', reason=str(e)) from e
        except Exception as e:
            if upload_stream is not None:
                try:
                    await upload_stream.abort()
                except Exception:
                    pass
            logger.error(
                'Failed to upload file to GridFS',
                filename=file.filename,
                bucket=self._bucket_name.value,
                error=str(e),
            )
            raise FileUploadError(filename=file.filename or 'unknown', reason=str(e)) from e

    async def download(self, file_id: UUID) -> AsyncGenerator[bytes, None]:
        """从 GridFS 下载文件（流式）"""
        bucket = await self._get_bucket()
        file_id_str = str(file_id)

        try:
            if not await self.exists(file_id):
                raise FileNotFoundError(file_id=file_id_str)

            grid_out = await bucket.open_download_stream(file_id_str)
            chunk_size = 1024 * 1024
            while True:
                chunk = await grid_out.read(chunk_size)
                if not chunk:
                    break
                yield chunk

            logger.info(
                'File downloaded from GridFS',
                file_id=file_id_str,
                bucket=self._bucket_name.value,
            )

        except PyMongoError as e:
            if 'not found' in str(e).lower() or 'no such file' in str(e).lower():
                logger.warning(
                    'File not found in GridFS',
                    file_id=file_id_str,
                    bucket=self._bucket_name.value,
                )
                raise FileNotFoundError(file_id_str) from e
            logger.error(
                'MongoDB error during download',
                file_id=file_id_str,
                bucket=self._bucket_name.value,
                error=str(e),
            )
            raise FileDownloadError(file_id=file_id_str, reason=str(e)) from e
        except Exception as e:
            logger.error(
                'Failed to download file from GridFS',
                file_id=file_id_str,
                bucket=self._bucket_name.value,
                error=str(e),
            )
            raise FileDownloadError(file_id=file_id_str, reason=str(e)) from e

    async def delete(self, file_id: UUID) -> bool:
        """从 GridFS 删除文件"""
        bucket = await self._get_bucket()
        file_id_str = str(file_id)

        try:
            if not await self.exists(file_id):
                logger.warning(
                    'File not found for deletion',
                    file_id=file_id_str,
                    bucket=self._bucket_name.value,
                )
                return False

            await bucket.delete(file_id_str)
            logger.info(
                'File deleted from GridFS',
                file_id=file_id_str,
                bucket=self._bucket_name.value,
            )
            return True

        except PyMongoError as e:
            logger.error(
                'MongoDB error during deletion',
                file_id=file_id_str,
                bucket=self._bucket_name.value,
                error=str(e),
            )
            raise FileDeletionError(file_id=file_id_str, reason=str(e)) from e
        except Exception as e:
            logger.error(
                'Failed to delete file from GridFS',
                file_id=file_id_str,
                bucket=self._bucket_name.value,
                error=str(e),
            )
            raise FileDeletionError(file_id=file_id_str, reason=str(e)) from e

    async def exists(self, file_id: UUID) -> bool:
        """检查文件是否存在于 GridFS"""
        file_id_str = str(file_id)

        try:
            files_collection = await self._get_files_collection()
            doc = await files_collection.find_one({'_id': file_id_str})
            return doc is not None
        except PyMongoError as e:
            logger.error('GridFS exists check failed', file_id=file_id_str, error=str(e))
            return False
        except Exception:
            # 备用方法：尝试直接打开下载流
            try:
                bucket = await self._get_bucket()
                await bucket.open_download_stream(file_id_str)
                return True
            except Exception as e2:
                logger.error(f'GridFS file not found: {e2}')
                return False

    async def get_metadata(self, file_id: UUID) -> dict[str, Any]:
        """获取文件元数据（包含顶级 md5 和 contentType）"""
        file_id_str = str(file_id)
        try:
            files_collection = await self._get_files_collection()
            doc = await files_collection.find_one({'_id': file_id_str})

            if not doc:
                logger.warning(
                    'File metadata not found',
                    file_id=file_id_str,
                    bucket=self._bucket_name.value,
                )
                raise FileNotFoundError(file_id_str)

            # 构建返回字典，包含顶级字段
            return {
                'file_id': str(doc['_id']),
                'filename': doc.get('filename'),
                'length': doc.get('length', 0),
                'chunk_size': doc.get('chunkSize', 255 * 1024),
                'upload_date': doc.get('uploadDate'),
                'md5': doc.get('md5'),  # 顶级 MD5
                'content_type': doc.get('contentType'),  # 顶级 contentType
                'metadata': doc.get('metadata', {}),  # 嵌套的用户自定义元数据
            }

        except FileNotFoundError:
            raise
        except PyMongoError as e:
            logger.error(
                'MongoDB error while getting metadata',
                file_id=file_id_str,
                bucket=self._bucket_name.value,
                error=str(e),
            )
            raise StorageConnectionError(backend='GridFS', reason=str(e)) from e
        except Exception as e:
            logger.error(
                'Failed to get file metadata from GridFS',
                file_id=file_id_str,
                bucket=self._bucket_name.value,
                error=str(e),
            )
            raise StorageConnectionError(backend='GridFS', reason=str(e)) from e
