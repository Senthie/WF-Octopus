"""
Author: '浪川' '1214391613@qq.com'
Date: 2026-04-22 17:27:29
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-04-22 17:43:53
FilePath: /api/app/scheams/inspection_requirement_scheam.py
Description:

Copyright (c) 2026 by '浪川' email: '1214391613@qq.com', All Rights Reserved.
"""

from pydantic import BaseModel, Field


class InspectionRequirementIn(BaseModel):
    """
    巡检要求明细表传入模型
    """

    item_name: str = Field(description='巡检项目名称')
    safety_requirement: str = Field(description='安全要求')
