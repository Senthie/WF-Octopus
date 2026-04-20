"""
Author: '浪川' '1214391613@qq.com'
Date: 2026-04-20 15:34:27
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-04-20 16:05:38
FilePath: /api/app/models/ai_inspection/__init__.py
Description: 模块初始化

Copyright (c) 2026 by '浪川' email: '1214391613@qq.com', All Rights Reserved.
"""

from app.models.ai_inspection.ai_inspection_model import (
    AiExecuteTaskModel,
    InspectionRecordModel,
    InspectionRequirementModel,
)

__all__ = [
    'AiExecuteTaskModel',
    'InspectionRecordModel',
    'InspectionRequirementModel',
]
