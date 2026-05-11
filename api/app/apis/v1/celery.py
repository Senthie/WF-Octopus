"""
Author: '浪川' '1214391613@qq.com'
Date: 2026-04-27 17:27:26
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-05-11 14:56:34
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
from app.tasks.example_task import async_demo, example_task
from app.tasks.ollama_task import ollama_generate
from app.utils.celery_db_help import CeleryDbHelp

router = APIRouter(prefix='/celery', tags=['A celery test api'])

# 依赖注入定义
DbSession = Annotated[AsyncSession, Depends(get_session)]
Redis = Annotated[RedisClient, Depends(get_redis)]


def get_celery_db_help(db: DbSession) -> CeleryDbHelp:
    """获取认证服务实例"""
    return CeleryDbHelp(db)


UserServiceDep = Annotated[CeleryDbHelp, Depends(get_celery_db_help)]


@router.post(
    '/test',
    summary='test',
)
async def test(
    name: str,
) -> ResponseModel:
    """ """
    try:
        task = example_task.delay(name=name)
        return response_base.success(
            res=CustomResponseCodeEnum.SUCCESS,
            data={'task_id': task.id, 'status': 'queued'},
        )
    except Exception as e:
        # 返回未知异常的响应格式
        return response_base.fail(
            res=CustomResponseCodeEnum.UNKNOWN_ERROR,
            data=str(e),
        )


@router.post('/fetch')
async def fetch_url(name: str):
    task = async_demo.delay(name)

    return response_base.success(
        res=CustomResponseCodeEnum.SUCCESS,
        data={'task_id': task.id, 'status': 'queued'},
    )


@router.get('/fetch/{task_id}')
async def get_fetch_result(task_id: str):
    from celery.result import AsyncResult

    from app.core.celery import celery_app

    result = AsyncResult(task_id, app=celery_app)
    if result.ready():
        return {'status': result.status, 'result': result.result}
    return {'status': result.status}


class OllamaRequest(BaseModel):
    prompt: str
    model: str = 'llama2'


@router.post('/generate')
async def generate(req: OllamaRequest, service: UserServiceDep):
    # 发送 Celery 异步任务
    task = ollama_generate.delay(req.prompt, req.model)
    task_id = task.id

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
async def status(task_id: str, service: UserServiceDep):
    record = await service.get_task_record(task_id)
    if not record:
        raise HTTPException(404, 'Task not found')
    return {
        'task_id': record.task_id,
        'status': record.status,
        'result': record.result,
        'error': record.error,
        # 'duration_seconds': record.started_at - record.ended_at,
    }
