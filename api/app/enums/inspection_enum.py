"""
Author: '浪川' '1214391613@qq.com'
Date: 2026-04-17 16:45:09
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-04-20 10:36:58
FilePath: /api/app/enums/inspection_enum.py
Description: 巡检相关的枚举类


Copyright (c) 2026 by '浪川' email: '1214391613@qq.com', All Rights Reserved.
"""

from enum import Enum


class InspectionResultEnum(Enum):
    """巡检结果枚举类状态码"""

    NORMAL = 'normal'  # 正常

    REQUIRES_CORRECTION = 'requires_correction'  # 需要整改
    IN_PROGRESS = 'in_progress'  # 进行中
    COMPLETED = 'corrected'  # 已经整改
