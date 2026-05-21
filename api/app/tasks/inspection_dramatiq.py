"""
Author: '浪川' '1214391613@qq.com'
Date: 2026-05-12 17:23:09
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-05-21 09:35:19
FilePath: /api/app/tasks/inspection_dramatiq.py
Description: Dramatiq async actor for AI inspection task.

This module provides an `async` actor that can be run by a dramatiq worker.
It mirrors the logic in the Celery task but is fully async and uses the
existing async services and drivers.

Copyright (c) 2026 by '浪川' email: '1214391613@qq.com', All Rights Reserved.
"""

from __future__ import annotations

from datetime import datetime
import traceback
from typing import Optional
from uuid import UUID

import dramatiq
import httpx
import json_repair

from app.core import dramatiq as dramatiq_config  # noqa: F401
from app.core.config import settings
from app.core.logging import get_logger
from app.core.mongodb import mongodb_client
from app.core.pg_database import AsyncSessionLocal
from app.enums.inspection_enum import InspectionResultEnum
from app.models.auth.user import UserModel
from app.models.task_record import TaskStatus
from app.schemas import InspectionRecordOut, InspectionRequirementOut
from app.services.ai_inspection_service import AiInspectionService
from app.services.file_service import FileService
from app.services.task_record_service import TaskRecordService
from app.utils.timezone_help import tz_helper

logger = get_logger(__name__)


async def _update_task_record(
    id: UUID,
    *,
    status: TaskStatus,
    result: Optional[dict] = None,
    error: Optional[str] = None,
    task_name: Optional[str] = None,
    task_kwargs: Optional[dict] = None,
    started_at: Optional[datetime] = None,
    ended_at: Optional[datetime] = None,
) -> None:
    """安全地更新任务记录状态，自身异常不会掩盖原始业务异常。"""
    if not id:
        return

    payload: dict = {'status': status}
    if task_name is not None:
        payload['task_name'] = task_name
    if task_kwargs is not None:
        payload['kwargs'] = task_kwargs
    if result is not None:
        payload['result'] = result
    if error is not None:
        payload['error'] = error
    if started_at is not None:
        payload['started_at'] = started_at
    if ended_at is not None:
        payload['ended_at'] = ended_at
    else:
        payload.setdefault('ended_at', tz_helper.get_current_time('Asia/Shanghai'))

    try:
        async with AsyncSessionLocal() as session:
            service = TaskRecordService(session)
            await service.update_by_id(id, **payload)
    except Exception:
        logger.exception(f'Failed to update task record {id}')


async def _call_ollama(
    prompt: str,
    images: Optional[list[str]] = None,
    timeout: float = 605.0,
) -> str:
    """调用 Ollama API，返回纯文本响应。"""
    payload = {
        'model': settings.ollama_model,
        'prompt': prompt,
        'stream': False,
    }
    if images:
        payload['images'] = images

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            # f'{settings.ollama_host}/api/generate',
            'http://14.12.0.172:19516/api/generate',
            json=payload,
            timeout=timeout,
        )
        resp.raise_for_status()
        return resp.json().get('response', '') or ''


async def _perform_image_detection(
    record: InspectionRecordOut,
    requirement: InspectionRequirementOut,
) -> Optional[str]:
    """第一阶段：基于现场照片进行 AI 视觉检测。"""
    task_id = record.ai_detection_execute_id

    await _update_task_record(
        task_id,
        status=TaskStatus.STARTED,
        task_name='ai_inspection_task',
        task_kwargs={
            'record': record.model_dump_json(),
            'inspection_requirement': requirement.model_dump_json(),
        },
        started_at=tz_helper.get_current_time('Asia/Shanghai'),
    )

    try:
        async with AsyncSessionLocal() as session:
            file_service = FileService(session)
            image_base64 = await file_service.get_image_base64_from_storage(record.file_id)

        prompt = (
            f'请根据现场照片，识别具体情况，并按以下安全要求进行检查确认：\n'
            f'{requirement.item_name}: {requirement.safety_requirement}\n'
            f'每项检查都需要单独确认是否有问题，如果有问题，请具体描述。按以下结构输出检查结果：\n'
            f'1. {requirement.item_name}:\n'
        )

        detection_result = await _call_ollama(prompt, images=[image_base64])
        if not detection_result:
            raise ValueError('Ollama returned empty response for image detection')

        await _update_task_record(
            task_id,
            status=TaskStatus.SUCCESS,
            result={'response': detection_result},
        )
        logger.info(f'AI image detection completed: {detection_result[:200]}...')
        return detection_result

    except Exception:
        error_msg = traceback.format_exc()
        logger.exception('Image detection phase failed')
        await _update_task_record(task_id, status=TaskStatus.FAILURE, error=error_msg)
        raise


async def _extract_and_save_result(
    record: InspectionRecordOut,
    requirement: InspectionRequirementOut,
    user: UserModel,
    detection_result: str,
) -> None:
    """第二阶段：提取结构化结果并持久化到数据库。"""
    task_id = record.ai_inspection_excute_id  # 注意：保持与模型字段名一致

    await _update_task_record(
        task_id,
        status=TaskStatus.STARTED,
        task_name='ai_inspection_task',
        task_kwargs={
            'record': record.model_dump_json(),
            'inspection_requirement': requirement.model_dump_json(),
        },
        started_at=tz_helper.get_current_time('Asia/Shanghai'),
    )

    try:
        prompt = (
            '你是一位安全合规数据提取专家。请从输入的安全检查文本中，仅提取两项信息：\n\n'
            '1. **result（检查结果）**：用一句话概括客观检查结论，去除主观评价和冗余背景，保留核心事实。\n'
            '2. **status（整改状态）**：根据检查结果判断\n'
            '   - `normal`：检查合格、符合要求、无隐患\n'
            '   - `requires_correction`：存在不符合项、未设置、缺失、有隐患、需整改\n\n'
            '**输出要求：**\n'
            '- 必须且仅返回如下 JSON 对象，不要任何解释、注释或 markdown 代码块标记\n'
            '- 格式严格为：{"status": "normal 或 requires_correction", "result": "提取的检查结果"}\n\n'
            '**提取规则：**\n'
            '- result 只保留"发现了什么/未设置什么/状态如何"，去掉"存在安全隐患"、'
            '"不符合安全要求"等推论性语句，除非原文无具体事实仅有推论。\n'
            '- 若文本中包含"未设置"、"未发现"、"不符合"、"缺失"、"无...标识"等负面描述，'
            'status 必须为 requires_correction。\n'
            '- 若文本明确说明"符合"、"正常"、"完好"，status 为 normal。\n\n'
            '**示例：**\n'
            '输入：安全标识检查结果：未发现清晰、完好的安全标识（如紧急停止标志、警告标志等），'
            '现场环境未显示相关安全标识的设置。\n'
            '输出：{"status": "requires_correction", "result": "未发现清晰完好的安全标识，现场未设置相关安全标识"}\n\n'
            f'现在请处理以下文本，从中提取「{requirement.item_name}」的检查结果：\n{detection_result}'
        )

        response_text = await _call_ollama(prompt)
        if not response_text:
            raise ValueError('Ollama returned empty response for result extraction')

        # 解析并严格校验结构
        try:
            ai_inspection = json_repair.loads(response_text)
        except Exception as parse_err:
            logger.error(f'JSON repair failed for response: {response_text[:500]}')
            raise ValueError(f'Failed to parse AI response as JSON: {parse_err}') from parse_err

        if not isinstance(ai_inspection, dict):
            raise ValueError(
                f'Expected dict from AI, got {type(ai_inspection).__name__}: {ai_inspection}'
            )

        await _update_task_record(
            task_id,
            status=TaskStatus.SUCCESS,
            result=ai_inspection,
        )

        # 更新巡检记录最终状态
        status_enum = (
            InspectionResultEnum.NORMAL
            if ai_inspection.get('status') == 'normal'
            else InspectionResultEnum.REQUIRES_CORRECTION
        )

        async with AsyncSessionLocal() as session:
            inspection_service = AiInspectionService(session)
            await inspection_service.patch_data_by_id(
                record.id,
                data={'status': status_enum},
                user=user,
            )

    except Exception:
        error_msg = traceback.format_exc()
        logger.exception('Result extraction phase failed')
        await _update_task_record(task_id, status=TaskStatus.FAILURE, error=error_msg)
        raise


@dramatiq.actor(queue_name='ai_inspection', max_retries=3)
async def ai_inspection_task_async(
    record: str,
    inspection_requirement: str,
    user: str,
) -> None:
    """Dramatiq 异步 Actor：执行 AI 巡检任务。

    分为两个阶段：
    1. 图像识别：调用 Ollama 视觉模型分析现场照片；
    2. 结果提取：将非结构化描述转为结构化数据并入库。
    """
    await mongodb_client.connect()

    try:
        record_model = InspectionRecordOut.model_validate_json(record)
        requirement_model = InspectionRequirementOut.model_validate_json(inspection_requirement)
        user_model = UserModel.model_validate_json(user)
    except Exception:
        logger.exception('Failed to parse input JSON')
        raise

    # 阶段一：图片检测
    detection_result = await _perform_image_detection(record_model, requirement_model)
    if not detection_result:
        logger.warning('No detection result produced, skipping extraction phase')
        return

    # 阶段二：结构化提取与持久化
    await _extract_and_save_result(record_model, requirement_model, user_model, detection_result)
