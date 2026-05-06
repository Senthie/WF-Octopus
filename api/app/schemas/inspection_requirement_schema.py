"""
Author: '浪川' '1214391613@qq.com'
Date: 2026-04-22 17:27:29
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-05-06 15:02:26
FilePath: /api/app/schemas/inspection_requirement_schema.py
Description:

Copyright (c) 2026 by '浪川' email: '1214391613@qq.com', All Rights Reserved.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class InspectionRequirementIn(BaseModel):
    """
    巡检要求明细表传入模型
    """

    item_name: str = Field(description='巡检项目名称')
    safety_requirement: str = Field(description='安全要求')


class InspectionRequirementOut(BaseModel):
    """
    巡检要求明细表传出模型
    """

    model_config = {'from_attributes': True}

    id: UUID = Field(description='唯一标识符')
    created_by: UUID = Field(..., description='创建者')
    created_at: Optional[datetime] = Field(..., description='创建时间')
    updated_at: datetime | None = Field(description='更新时间')
    updated_by: UUID = Field(..., description='最后更新者')

    item_name: str = Field(description='巡检项目名称')
    safety_requirement: str = Field(description='安全要求')
