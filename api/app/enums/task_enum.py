"""
Author: '浪川' '1214391613@qq.com'
Date: 2026-04-17 16:16:04
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-05-15 11:50:01
FilePath: /api/app/enums/task_enum.py
Description: 封装简单的任务状态

Copyright (c) 2026 by '浪川' email: '1214391613@qq.com', All Rights Reserved.
"""

from enum import Enum


class TaskStatusEnum(Enum):
    """任务状态码"""

    PENDING = 'pending'  # 待处理

    PROCESSING = 'processing'  # 处理中

    COMPLETED = 'completed'  # 已完成

    FAILED = 'failed'  # 错误


class DramatiqTaskStatus(str, Enum):
    PENDING = 'pending'
    STARTED = 'started'
    SUCCESS = 'success'
    FAILURE = 'failure'
    RETRY = 'retry'
    REVOKED = 'revoked'
