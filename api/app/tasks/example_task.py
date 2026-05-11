"""
Author: '浪川' '1214391613@qq.com'
Date: 2026-05-09 14:57:09
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-05-11 10:29:49
FilePath: /api/app/tasks/example_task.py
Description:

Copyright (c) 2026 by '浪川' email: '1214391613@qq.com', All Rights Reserved.
"""

import asyncio
import time

from app.core.celery import celery_app
from app.core.logging import get_logger

logger = get_logger(__name__)


# 这是一个同步任务示例
@celery_app.task(name='example_task')
def example_task(name: str, seconds: int = 5):
    """模拟耗时操作"""
    time.sleep(seconds)
    logger.info(f'Hello {name}, task finished after {seconds} seconds.')
    return f'Hello {name}, task finished after {seconds} seconds.'


# 如果你的任务需要调用异步代码（如 httpx，async DB 操作）
# 可以使用 asyncio.run() 包装，或者将 Celery worker 运行在 asyncio 池中（高级）
@celery_app.task(name='async_demo')
def async_demo(name: str, seconds: int = 5):
    async def _fetch():
        time.sleep(seconds)

        return f'Hello {name}, task finished after {seconds} seconds.'

    return asyncio.run(_fetch())


@celery_app.task(name='post_ollama')
def async_post_ollama(name: str, seconds: int = 5):
    async def _fetch():
        time.sleep(seconds)

        return f'Hello {name}, task finished after {seconds} seconds.'

    return asyncio.run(_fetch())
