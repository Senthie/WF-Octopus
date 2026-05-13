"""Dramatiq async actor for AI inspection task.

This module provides an `async` actor that can be run by a dramatiq worker.
It mirrors the logic in the Celery task but is fully async and uses the
existing async services and drivers.
"""

from __future__ import annotations

import traceback
from uuid import UUID

import dramatiq
import httpx

# Ensure broker and uvloop are configured
from app.core import dramatiq as dramatiq_config  # noqa: F401
from app.core.config import settings
from app.core.logging import get_logger
from app.core.mongodb import mongodb_client
from app.core.pg_database import AsyncSessionLocal
from app.models.task_record import TaskStatus
from app.schemas import InspectionRecordOut, InspectionRequirementOut
from app.services.file_service import FileService
from app.services.task_record_service import TaskRecordService
from app.utils.timezone_help import tz_helper

logger = get_logger(__name__)


@dramatiq.actor(queue_name='ai_inspection', max_retries=3)
async def ai_inspection_task_async(record: str, inspection_requirement: str, task_record_id: str):
    """Async actor to perform AI inspection work.

    Args:
        record: JSON string of InspectionRecordOut
        inspection_requirement: JSON string of InspectionRequirementOut
        task_record_id: UUID string for the task record (optional)
    """
    try:
        await mongodb_client.connect()
        if task_record_id:
            async with AsyncSessionLocal() as session:
                server = TaskRecordService(session)
                await server.update_by_id(
                    UUID(task_record_id),
                    **{
                        'task_name': 'ai_inspection_task',
                        'kwargs': {
                            'record': record,
                            'inspection_requirement': inspection_requirement,
                        },
                        'status': TaskStatus.STARTED,
                        'started_at': tz_helper.get_current_time('Asia/Shanghai'),
                    },
                )

        record_model: InspectionRecordOut = InspectionRecordOut.model_validate_json(record)
        inspection_requirement_model: InspectionRequirementOut = (
            InspectionRequirementOut.model_validate_json(inspection_requirement)
        )

        # 获取图像并调用 Ollama
        async with AsyncSessionLocal() as session:
            file_service = FileService(session)
            image_base64 = await file_service.get_image_base64_from_storage(record_model.file_id)

        prompt1 = f'请根据现场照片，识别具体情况，并按以下安全要求进行检查确认：{inspection_requirement_model.item_name}:{inspection_requirement_model.safety_requirement}'
        payload = {
            'model': settings.ollama_model,
            'prompt': prompt1,
            'stream': False,
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f'{settings.ollama_host}/api/generate', json=payload, timeout=605
            )
            resp.raise_for_status()
            result = resp.json()

        if task_record_id:
            async with AsyncSessionLocal() as session:
                server = TaskRecordService(session)
                await server.update_by_id(
                    UUID(task_record_id),
                    **{
                        'status': TaskStatus.SUCCESS,
                        'result': {'answer': result},
                        'ended_at': tz_helper.get_current_time('Asia/Shanghai'),
                    },
                )

        return result.get('response', 'No response field')

    except Exception:
        error_msg = traceback.format_exc()
        logger.exception('ai_inspection_task_async failed')
        if task_record_id:
            async with AsyncSessionLocal() as session:
                server = TaskRecordService(session)
                await server.update_by_id(
                    id=UUID(task_record_id),
                    **{
                        'status': TaskStatus.FAILURE,
                        'error': error_msg,
                        'ended_at': tz_helper.get_current_time('Asia/Shanghai'),
                    },
                )
        raise
