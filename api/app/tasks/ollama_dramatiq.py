"""
Author: '浪川' '1214391613@qq.com'
Date: 2026-05-12 17:30:29
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-05-13 10:33:40
FilePath: /api/app/tasks/ollama_dramatiq.py
Description: Dramatiq async actor for Ollama generate task.

Copyright (c) 2026 by '浪川' email: '1214391613@qq.com', All Rights Reserved.
"""

from __future__ import annotations

import traceback

import dramatiq
import httpx

from app.core.config import settings
from app.core.logging import get_logger
from app.core.mongodb import mongodb_client
from app.core.pg_database import AsyncSessionLocal
from app.models.task_record import TaskStatus
from app.services.task_record_service import TaskRecordService
from app.utils.timezone_help import tz_helper

logger = get_logger(__name__)


@dramatiq.actor(queue_name='ollama', store_results=True)
async def ollama_generate_async(
    prompt: str, model: str = 'llama2', image_base64: str = '', task_record_id: str = ''
):
    task_id = task_record_id or None
    try:
        await mongodb_client.connect()
        if task_id:
            async with AsyncSessionLocal() as session:
                server = TaskRecordService(session)
                await server.update_task_status_by_task_id(
                    task_id,
                    TaskStatus.STARTED,
                    started_at=tz_helper.get_current_time('Asia/Shanghai'),
                )

        payload = {
            'model': settings.ollama_model,
            'prompt': prompt,
            'stream': False,
            'images': [image_base64] if image_base64 else [],
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f'{settings.ollama_host}/api/generate', json=payload, timeout=15.0
            )
            resp.raise_for_status()
            result = resp.json()

        if task_id:
            async with AsyncSessionLocal() as session:
                server = TaskRecordService(session)
                await server.update_task_status_by_task_id(
                    task_id,
                    TaskStatus.SUCCESS,
                    result={'answer': result},
                    ended_at=tz_helper.get_current_time('Asia/Shanghai'),
                )

        return result.get('response', 'No response field')

    except Exception:
        error_msg = traceback.format_exc()
        logger.exception('ollama_generate_async failed')
        if task_id:
            async with AsyncSessionLocal() as session:
                server = TaskRecordService(session)
                await server.update_task_status_by_task_id(
                    task_id,
                    TaskStatus.FAILURE,
                    error=error_msg,
                    ended_at=tz_helper.get_current_time('Asia/Shanghai'),
                )
        raise
