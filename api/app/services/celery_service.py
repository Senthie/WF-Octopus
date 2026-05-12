"""
Author: '浪川' '1214391613@qq.com'
Date: 2026-05-11 12:16:09
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-05-12 11:59:14
FilePath: /api/app/services/celery_service.py
Description: celery 数据库操作辅助函数

Copyright (c) 2026 by '浪川' email: '1214391613@qq.com', All Rights Reserved.
"""

# app/db/celery_task_dao.py
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import CeleryTaskRecordModel, CeleryTaskStatus


class CeleryTaskRecordService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_task_record(
        self,
        task_id: str,
        task_name: str,
        args: Optional[List[Any]] = None,
        kwargs: Optional[Dict[str, Any]] = None,
        related_record_id: Optional[UUID] = None,
    ) -> CeleryTaskRecordModel:
        """创建任务记录（通常由发送任务时调用）"""
        record = CeleryTaskRecordModel(
            task_id=task_id,
            task_name=task_name,
            args=args,
            kwargs=kwargs,
            status=CeleryTaskStatus.PENDING,
            related_record_id=related_record_id,
            created_by=uuid4(),
        )
        self.db.add(record)
        await self.db.commit()
        await self.db.refresh(record)
        return record

    async def update_task_status_by_task_id(
        self,
        task_id: str,
        status: CeleryTaskStatus,
        result: Optional[Any] = None,
        error: Optional[str] = None,
        started_at: Optional[datetime] = None,
        ended_at: Optional[datetime] = None,
    ) -> Optional[CeleryTaskRecordModel]:
        """更新任务状态和结果"""
        stmt = select(CeleryTaskRecordModel).where(CeleryTaskRecordModel.task_id == task_id)
        result_db = await self.db.execute(stmt)
        record = result_db.scalar_one_or_none()
        if not record:
            return None

        record.status = status
        if result is not None:
            record.result = result
        if error is not None:
            record.error = error
        if started_at:
            record.started_at = started_at
        if ended_at:
            record.ended_at = ended_at

        await self.db.commit()
        await self.db.refresh(record)
        return record

    async def update_by_id(
        self,
        id: UUID,
        task_id: str = '',
        task_name: str = '',
        args: list | None = None,
        kwargs: dict | None = None,
        status: CeleryTaskStatus = CeleryTaskStatus.PENDING,
        result: Optional[Any] = None,
        error: Optional[str] = None,
        started_at: Optional[datetime] = None,
        ended_at: Optional[datetime] = None,
    ) -> Optional[CeleryTaskRecordModel]:
        """更新任务状态和结果"""
        stmt = select(CeleryTaskRecordModel).where(CeleryTaskRecordModel.id == id)
        result_db = await self.db.execute(stmt)
        record = result_db.scalar_one_or_none()
        if not record:
            return None
        # 设置celer 的任务id
        record.task_id = task_id

        # 设置 celery的任务名
        task_name = task_name
        # 设置 参数
        record.args = args
        record.kwargs = kwargs

        record.status = status
        if result is not None:
            record.result = result
        if error is not None:
            record.error = error
        if started_at:
            record.started_at = started_at
        if ended_at:
            record.ended_at = ended_at

        await self.db.commit()
        await self.db.refresh(record)
        return record

    async def get_task_record_by_task_id(self, task_id: str) -> Optional[CeleryTaskRecordModel]:
        stmt = select(CeleryTaskRecordModel).where(CeleryTaskRecordModel.task_id == task_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
