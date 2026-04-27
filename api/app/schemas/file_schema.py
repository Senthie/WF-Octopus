"""
Author: '浪川' '1214391613@qq.com'
Date: 2026-04-27 09:59:21
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-04-27 11:28:08
FilePath: /api/app/schemas/file_schema.py
Description:

Copyright (c) 2026 by '浪川' email: '1214391613@qq.com', All Rights Reserved.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class FileReferenceOut(BaseModel):
    """
    执行记录输出模型
    """

    model_config = {'from_attributes': True}

    id: UUID = Field(default_factory=uuid4)  # 唯一标识符
    created_at: Optional[datetime] = Field(..., description='创建时间')
    updated_at: Optional[datetime] = Field(..., description='更新时间')

    gridfs_id: UUID = Field(..., description='GridFS文件ID')
    filename: str = Field(max_length=255, description='文件名')
    content_type: str = Field(max_length=100, description='文件类型')
    size_bytes: int
    storage_type: str = Field(
        ..., description='存储类型（MONGODB-小文件/GRIDFS-大文件）'
    )  # MONGODB, GRIDFS
    uploaded_by: UUID = Field(..., description='Logical FK to users')
