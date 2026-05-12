"""Task record DB helper (replaces celery_service naming)."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import TaskRecordModel, TaskStatus


class TaskRecordService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_task_record(
        self,
        task_id: str,
        task_name: str,
        args: Optional[List[Any]] = None,
        kwargs: Optional[Dict[str, Any]] = None,
        related_record_id: Optional[UUID] = None,
    ) -> TaskRecordModel:
        record = TaskRecordModel(
            task_id=task_id if len(task_id) > 0 else str(uuid4()),
            task_name=task_name,
            args=args,
            kwargs=kwargs,
            status=TaskStatus.PENDING,
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
        status: TaskStatus,
        result: Optional[Any] = None,
        error: Optional[str] = None,
        started_at: Optional[datetime] = None,
        ended_at: Optional[datetime] = None,
    ) -> Optional[TaskRecordModel]:
        stmt = select(TaskRecordModel).where(TaskRecordModel.task_id == task_id)
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
        status: TaskStatus = TaskStatus.PENDING,
        result: Optional[Any] = None,
        error: Optional[str] = None,
        started_at: Optional[datetime] = None,
        ended_at: Optional[datetime] = None,
    ) -> Optional[TaskRecordModel]:
        stmt = select(TaskRecordModel).where(TaskRecordModel.id == id)
        result_db = await self.db.execute(stmt)
        record = result_db.scalar_one_or_none()
        if not record:
            return None

        record.task_id = task_id
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

    async def get_task_record_by_task_id(self, task_id: str) -> Optional[TaskRecordModel]:
        stmt = select(TaskRecordModel).where(TaskRecordModel.task_id == task_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
