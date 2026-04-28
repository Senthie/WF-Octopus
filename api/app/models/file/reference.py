"""
Author: '浪川' '1214391613@qq.com'
Date: 2026-04-24 12:25:21
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-04-27 12:20:42
FilePath: /api/app/models/file/reference.py
Description:

Copyright (c) 2026 by '浪川' email: '1214391613@qq.com', All Rights Reserved.
"""

from uuid import UUID

from sqlmodel import Field

from app.models.base_mixin import (
    AuditMixin,
    BaseModel as MyBaseModel,
    SoftDeleteMixin,
    TimestampMixin,
)


class FileReferenceModel(MyBaseModel, TimestampMixin, SoftDeleteMixin, AuditMixin, table=True):
    """文件引用表 - PostgreSQL中的文件引用。

    在PostgreSQL中存储文件的元数据和引用信息。
    实际文件内容存储在MongoDB中（使用GridFS处理大文件）。

    Attributes:
    已经继承
        id: 文件引用记录唯一标识符（UUID）
        workspace_id: 所属工作空间ID（逻辑外键，租户隔离）
        created_at: 创建时间
        deleted_at: Optional[datetime] = Field(default=None)
        is_deleted: bool = Field(default=False)
        created_by : UUID
        updated_by : UUID

        file_id: 文件业务ID（UUID，关联到MongoDB）
        filename: 文件名
        content_type: 文件MIME类型
        size_bytes: 文件大小（字节）
        storage_type: 存储类型（MONGODB-小文件/GRIDFS-大文件）
        mongo_id: MongoDB文档ID或GridFS文件ID

    业务规则：
        - 小文件（< 16MB）直接存储在MongoDB文档中
        - 大文件（>= 16MB）使用GridFS分块存储
        - 文件删除时同时清理PostgreSQL引用和MongoDB数据
        - 支持按工作空间隔离文件访问
    """

    __tablename__ = 'file_references'  # type: ignore

    gridfs_id: UUID = Field(unique=True, index=True, description='GridFS文件ID')
    filename: str = Field(max_length=255, description='文件名')
    content_type: str = Field(max_length=100, description='文件类型')
    size_bytes: int
    storage_type: str = Field(
        max_length=20, index=True, description='存储类型（MONGODB-小文件/GRIDFS-大文件）'
    )  # MONGODB, GRIDFS
