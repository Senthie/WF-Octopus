"""
Author: '浪川' '1214391613@qq.com'
Date: 2026-05-11 12:01:12
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-05-11 14:52:11
FilePath: /api/app/models/celery.py
Description:

Copyright (c) 2026 by '浪川' email: '1214391613@qq.com', All Rights Reserved.
"""

# app/models/celery_task.py
from datetime import datetime
import enum
from typing import Optional
from uuid import UUID

from sqlalchemy import JSON, Text
from sqlmodel import Column, Field

from app.models.base_mixin import (
    AuditMixin,
    BaseModel as MyBaseModel,
    TimestampMixin,
)
from app.utils.timezone_help import tz_helper


class CeleryTaskStatus(str, enum.Enum):
    PENDING = 'pending'
    STARTED = 'started'
    SUCCESS = 'success'
    FAILURE = 'failure'
    RETRY = 'retry'
    REVOKED = 'revoked'


class CeleryTaskRecordModel(MyBaseModel, TimestampMixin, AuditMixin, table=True):
    __tablename__ = 'celery_task_records'  # type: ignore

    task_id: str = Field(unique=True, index=True, nullable=False)  # Celery 的任务 ID
    task_name: str = Field(index=True, nullable=False)  # 任务名称（如 "async_demo"）
    args: Optional[list] = Field(default=None, sa_column=Column(JSON))  # 位置参数
    kwargs: Optional[dict] = Field(default=None, sa_column=Column(JSON))  # 关键字参数
    status: CeleryTaskStatus = Field(default=CeleryTaskStatus.PENDING, index=True)
    result: Optional[dict] = Field(default=None, sa_column=Column(JSON))  # 结果（可序列化）
    error: Optional[str] = Field(
        default=None, sa_column=Column(Text)
    )  # 错误信息（traceback 或简略）
    worker_hostname: Optional[str] = None  # 执行任务的 worker 主机名（可选）
    started_at: Optional[datetime] = Field(
        default_factory=lambda: tz_helper.get_current_time('Asia/Shanghai')
    )
    ended_at: Optional[datetime] = None

    # 关联字段（可选），例如关联业务记录 ID
    related_record_id: Optional[UUID] = Field(default=None, index=True)
