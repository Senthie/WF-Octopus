"""
Author: '浪川' '1214391613@qq.com'
Date: 2026-04-20 17:44:34
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-04-23 12:08:54
FilePath: /api/app/scheams/__init__.py
Description: 导入前后端的数据模型


Copyright (c) 2026 by '浪川' email: '1214391613@qq.com', All Rights Reserved.
"""

from app.schemas.ai_inspection_schema import (
    InspectionRecordIn,
    InspectionRecordOut,
)
from app.schemas.inspection_requirement_schema import (
    InspectionRequirementIn,
    InspectionRequirementOut,
)
from app.schemas.page_schema import PageReq, PageRes

__all__ = [
    'InspectionRecordIn',
    'InspectionRecordOut',
    'InspectionRequirementIn',
    'InspectionRequirementOut',
    'PageReq',
    'PageRes',
]
