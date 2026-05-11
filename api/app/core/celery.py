"""
Author: '浪川' '1214391613@qq.com'
Date: 2026-05-09 11:06:05
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-05-09 14:31:26
FilePath: /api/app/core/celery.py
Description:

Celery Setting

Copyright (c) 2026 by '浪川' email: '1214391613@qq.com', All Rights Reserved.
"""

# app/core/celery.py
from celery import Celery

from app.core.config import settings

# 创建全局唯一的 Celery 应用实例
celery_app = Celery(
    'fastapi_celery',
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

# 配置
celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='Asia/Shanghai',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 分钟
    task_soft_time_limit=25 * 60,  # 25 分钟
    result_expires=3600,
)

# 自动发现任务（确保任务模块已存在）
celery_app.autodiscover_tasks(['app.tasks'], force=True)

# 手动导入任务模块以确保注册
try:
    from app.tasks import example_task

    print(f'Successfully imported tasks: {celery_app.tasks}')
except ImportError as e:
    print(f'Failed to import tasks: {e}')
