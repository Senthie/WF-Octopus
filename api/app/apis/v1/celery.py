"""
Author: '浪川' '1214391613@qq.com'
Date: 2026-04-27 17:27:26
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-05-09 15:43:46
FilePath: /api/app/apis/v1/celery.py
Description: 认证相关API端点

Copyright (c) 2026 by '浪川' email: '1214391613@qq.com', All Rights Reserved.
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.pg_database import get_session
from app.core.redis import RedisClient, get_redis
from app.core.response import ResponseModel, response_base
from app.enums.response_code_enum import CustomResponseCodeEnum
from app.tasks.example_task import async_demo, example_task

router = APIRouter(prefix='/celery', tags=['A celery test api'])

# 依赖注入定义
DbSession = Annotated[AsyncSession, Depends(get_session)]
Redis = Annotated[RedisClient, Depends(get_redis)]


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
