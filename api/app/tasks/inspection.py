"""
Author: '浪川' '1214391613@qq.com'
Date: 2026-05-12 10:30:32
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-05-12 16:58:15
FilePath: /api/app/tasks/inspection.py
Description:

Copyright (c) 2026 by '浪川' email: '1214391613@qq.com', All Rights Reserved.
"""

import asyncio
import traceback
from uuid import UUID

import httpx

from app.core.celery import celery_app
from app.core.config import settings
from app.core.logging import get_logger
from app.core.mongodb import mongodb_client
from app.core.pg_database import AsyncSessionLocal
from app.models.celery import CeleryTaskStatus
from app.schemas import InspectionRecordOut, InspectionRequirementOut
from app.services.celery_service import CeleryTaskRecordService
from app.services.file_service import FileService
from app.utils.timezone_help import tz_helper

logger = get_logger(__name__)


@celery_app.task(name='ai_inspection_task', bind=True)
def ai_inspection_task(
    self,
    record: str,
    inspection_requirement: str,
    task_record_id: UUID,
):
    """
    同步 Celery 任务，内部使用 asyncio.run 调用异步 Ollama 客户端。

    :param self: 任务实例（bind=True 时提供）
    :param prompt: 用户提示
    :param model: 模型名称
    :param task_record_id: 数据库记录 ID（用于更新状态）
    """
    #
    task_id = self.request.id  # Celery 任务 ID
    # 记录任务开始，便于排查何时被 worker 接收
    print(f'ai_inspection_task START {task_id}')
    # 创建一条新的记录
    record_model: InspectionRecordOut = InspectionRecordOut.model_validate_json(record)
    inspection_requirement_model: InspectionRequirementOut = (
        InspectionRequirementOut.model_validate_json(inspection_requirement)
    )

    async def _run():
        loop = asyncio.get_running_loop()
        print(f'Running loop: {loop}, closed: {loop.is_closed()}')  # 应显示 False
        await mongodb_client.connect()
        # 可选：更新数据库状态为 started
        if task_record_id:
            async with AsyncSessionLocal() as session:
                server = CeleryTaskRecordService(session)
                await server.update_by_id(
                    id=task_record_id,
                    task_id=task_id,
                    task_name='ai_inspection_task',
                    kwargs={
                        'record': record,
                        'inspection_requirement': inspection_requirement,
                    },
                    status=CeleryTaskStatus.STARTED,
                    started_at=tz_helper.get_current_time('Asia/Shanghai'),
                )
        try:
            # 进行第一次AI识别 组装提示词
            prompt1 = f'请根据现场照片，识别具体情况，并按以下安全要求进行检查确认：{inspection_requirement_model.item_name}:{inspection_requirement_model.safety_requirement}'
            # 获取检测照片
            async with AsyncSessionLocal() as session:
                file_service = FileService(session)
                image_base64 = await file_service.get_image_base64_from_storage(
                    record_model.file_id
                )
            payload = {
                'model': settings.ollama_model,
                'prompt': prompt1,
                'stream': False,
                'images': image_base64,  # 注意是列表
            }
            # 调用 Ollama
            resp = await httpx.AsyncClient().post(
                f'{settings.ollama_host}/api/generate',  # 使用config配置
                json=payload,
                timeout=60,
            )
            resp.raise_for_status()
            result = resp.json()

            if task_record_id:
                logger.info(f'end {task_id}')
                async with AsyncSessionLocal() as session:
                    server = CeleryTaskRecordService(session)
                    await server.update_task_status_by_task_id(
                        task_id,
                        CeleryTaskStatus.SUCCESS,
                        result={'answer': result},
                        ended_at=tz_helper.get_current_time('Asia/Shanghai'),
                    )
            return result.get('response', 'No response field')

        except Exception as e:
            error_msg = traceback.format_exc()
            if task_record_id:
                async with AsyncSessionLocal() as session:
                    server = CeleryTaskRecordService(session)
                    await server.update_task_status_by_task_id(
                        task_id,
                        CeleryTaskStatus.FAILURE,
                        error=error_msg,
                        ended_at=tz_helper.get_current_time('Asia/Shanghai'),
                    )
            # 可选：触发重试
            raise self.retry(exc=e, countdown=60, max_retries=3)

    return asyncio.run(_run())
