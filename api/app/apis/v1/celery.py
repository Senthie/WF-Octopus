"""
Author: '浪川' '1214391613@qq.com'
Date: 2026-04-27 17:27:26
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-05-12 12:05:42
FilePath: /api/app/apis/v1/celery.py
Description: 认证相关API端点

Copyright (c) 2026 by '浪川' email: '1214391613@qq.com', All Rights Reserved.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.pg_database import get_session
from app.core.redis import RedisClient, get_redis
from app.core.response import ResponseModel, response_base
from app.enums.response_code_enum import CustomResponseCodeEnum
from app.services.celery_service import CeleryTaskRecordService

# Use Dramatiq actors
from app.tasks.example_dramatiq import async_demo_async, example_task_async
from app.tasks.ollama_dramatiq import ollama_generate_async

router = APIRouter(prefix='/celery', tags=['A celery test api'])

# 依赖注入定义
DbSession = Annotated[AsyncSession, Depends(get_session)]
Redis = Annotated[RedisClient, Depends(get_redis)]


def get_celery_db_help(db: DbSession) -> CeleryTaskRecordService:
    """获取认证服务实例"""
    return CeleryTaskRecordService(db)


CeleryServiceDep = Annotated[CeleryTaskRecordService, Depends(get_celery_db_help)]


@router.post(
    '/test',
    summary='test',
)
async def test(
    name: str,
) -> ResponseModel:
    """ """
    try:
        message = example_task_async.send(name=name)
        task_id = getattr(message, 'message_id', str(message))
        return response_base.success(
            res=CustomResponseCodeEnum.SUCCESS,
            data={'task_id': task_id, 'status': 'queued'},
        )
    except Exception as e:
        return response_base.fail(
            res=CustomResponseCodeEnum.UNKNOWN_ERROR,
            data=str(e),
        )


@router.post('/fetch')
async def fetch_url(name: str):
    message = async_demo_async.send(name)
    task_id = getattr(message, 'message_id', str(message))

    return response_base.success(
        res=CustomResponseCodeEnum.SUCCESS,
        data={'task_id': task_id, 'status': 'queued'},
    )


@router.get('/fetch/{task_id}')
async def get_fetch_result(task_id: str, service: CeleryServiceDep):
    # Return status from task record stored in DB (Dramatiq message id stored as task_id)
    record = await service.get_task_record_by_task_id(task_id)
    if not record:
        raise HTTPException(404, 'Task not found')
    return {'status': record.status, 'result': record.result, 'error': record.error}


class OllamaRequest(BaseModel):
    prompt: str
    model: str = 'llama2'


@router.post('/generate')
async def generate(req: OllamaRequest, service: CeleryServiceDep):
    # 发送 Celery 异步任务
    message = ollama_generate_async.send(req.prompt, req.model)
    task_id = getattr(message, 'message_id', str(message))

    try:
        # 在数据库中记录任务（状态 pending）
        await service.create_task_record(
            task_id=task_id,
            task_name='ollama_generate',
            args=[req.prompt],
            kwargs={'model': req.model},
        )
    except Exception as e:
        # 如果数据库操作失败，仍然返回任务ID
        print(f'Database error: {e}')

    return {'task_id': task_id, 'status': 'pending'}


@router.get('/status/{task_id}')
async def status(task_id: str, service: CeleryServiceDep):
    record = await service.get_task_record_by_task_id(task_id)
    if not record:
        raise HTTPException(404, 'Task not found')
    return {
        'task_id': record.task_id,
        'status': record.status,
        'result': record.result,
        'error': record.error,
        # 'duration_seconds': record.started_at - record.ended_at,
    }
