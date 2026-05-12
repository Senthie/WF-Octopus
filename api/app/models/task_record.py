"""
Author: '浪川' '1214391613@qq.com'
Date: 2026-05-12 18:05:17
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-05-12 19:49:50
FilePath: /api/app/models/task_record.py
Description:

Task record model (replacement for Celery-named model).

This keeps the original DB table name `celery_task_records` for
backwards-compatibility with existing migrations/data.

Copyright (c) 2026 by '浪川' email: '1214391613@qq.com', All Rights Reserved.
"""

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


class TaskStatus(str, enum.Enum):
    PENDING = 'pending'
    STARTED = 'started'
    SUCCESS = 'success'
    FAILURE = 'failure'
    RETRY = 'retry'
    REVOKED = 'revoked'


class TaskRecordModel(MyBaseModel, TimestampMixin, AuditMixin, table=True):
    __tablename__ = 'celery_task_records'  # type: ignore

    task_id: str = Field(unique=True, index=True, nullable=False)
    task_name: str = Field(index=True, nullable=False)
    args: Optional[list] = Field(default=None, sa_column=Column(JSON))
    kwargs: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    status: TaskStatus = Field(default=TaskStatus.PENDING, index=True)
    result: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    error: Optional[str] = Field(default=None, sa_column=Column(Text))
    worker_hostname: Optional[str] = None
    started_at: Optional[datetime] = Field(
        default_factory=lambda: tz_helper.get_current_time('Asia/Shanghai')
    )
    ended_at: Optional[datetime] = None

    related_record_id: Optional[UUID] = Field(default=None, index=True)
