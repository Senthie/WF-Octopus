"""
Author: '浪川' '1214391613@qq.com'
Date: 2026-04-20 17:44:34
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-04-22 17:31:14
FilePath: /api/app/scheams/__init__.py
Description: 导入前后端的数据模型


Copyright (c) 2026 by '浪川' email: '1214391613@qq.com', All Rights Reserved.
"""

from app.scheams.ai_inspection_scheam import (
    InspectionRecordIn,
    InspectionRecordOut,
)
from app.scheams.inspection_requirement_scheam import (
    InspectionRequirementIn,
)

__all__ = ['InspectionRecordIn', 'InspectionRecordOut', 'InspectionRequirementIn']
