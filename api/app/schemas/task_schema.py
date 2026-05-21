"""
Author: '浪川' '1214391613@qq.com'
Date: 2026-05-15 11:48:06
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-05-15 17:46:29
FilePath: /api/app/schemas/task_schema.py
Description:

Copyright (c) 2026 by '浪川' email: '1214391613@qq.com', All Rights Reserved.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.enums.task_enum import DramatiqTaskStatus


class TaskRecordBaseOut(BaseModel):
    model_config = {'from_attributes': True}

    task_id: str = Field()
    task_name: str = Field()
    args: Optional[list] = Field()
    kwargs: Optional[dict] = Field()
    status: DramatiqTaskStatus = Field(
        default=DramatiqTaskStatus.PENDING,
    )
    result: Optional[dict] = Field()
    error: Optional[str] = Field()
    worker_hostname: Optional[str] = None
    started_at: Optional[datetime] = Field()
    ended_at: Optional[datetime] = None

    related_record_id: Optional[UUID] = Field(
        default=None,
    )
