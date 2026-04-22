"""
Author: '浪川' '1214391613@qq.com'
Date: 2026-04-21 15:38:24
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-04-21 17:04:05
FilePath: /api/app/enums/__init__.py
Description: 枚举类，用于定义巡检和任务的状态和结果。


Copyright (c) 2026 by '浪川' email: '1214391613@qq.com', All Rights Reserved.
"""

from app.enums.inspection_enum import InspectionResultEnum
from app.enums.response_code_enum import CustomResponseCodeEnum
from app.enums.task_enum import TaskStatusEnum

__all__ = ['InspectionResultEnum', 'TaskStatusEnum', 'CustomResponseCodeEnum']
