"""
Author: '浪川' '1214391613@qq.com'
Date: 2026-04-16 16:51:01
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-05-15 16:27:03
FilePath: /api/app/schemas/ai_inspection_schema.py
Description: Ai 巡检的web 输入输出模型

Copyright (c) 2026 by '浪川' email: '1214391613@qq.com', All Rights Reserved.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.enums.inspection_enum import InspectionResultEnum
from app.schemas.task_schema import TaskRecordBaseOut


class InspectionRecordOut(BaseModel):
    """
    执行记录输出模型
    """

    model_config = {'from_attributes': True}

    id: UUID = Field(default_factory=uuid4)  # 唯一标识符

    inspection_requirements_id: UUID = Field(..., description=' 巡检要求明细表的唯一标识符')
    status: InspectionResultEnum = Field(
        default=InspectionResultEnum.NORMAL, description='巡检的状态'
    )
    file_id: UUID = Field(description='图片id')

    ai_detection_execute_id: UUID = Field(..., description='AI 执行图片分析的结果')
    ai_inspection_excute_id: UUID = Field(..., description='Ai 提取的特定巡检项目结果的id')
    responsible_person: str = Field(..., description='区域负责人')

    created_by: UUID = Field(..., description='创建者')
    created_at: Optional[datetime] = Field(..., description='创建时间')
    updated_by: UUID = Field(..., description='最后更新人时间')
    updated_at: datetime | None = Field(description='更新时间')


class InspectionRecordIn(BaseModel):
    """
    执行记录传入模型
    """

    inspection_requirements_id: UUID = Field(..., description=' 巡检要求明细表的唯一标识符')
    file_id: UUID = Field(description='图片id')
    responsible_person: str = Field(..., description='区域负责人')


class InspectionRecordUpdateIn(BaseModel):
    """
    执行记录传入模型
    """

    inspection_requirements_id: UUID = Field(..., description=' 巡检要求明细表的唯一标识符')
    file_id: UUID = Field(description='图片id')
    responsible_person: str = Field(..., description='区域负责人')
    ai_detection_execute_id: Optional[UUID] = Field(..., description='AI 执行图片分析的结果')
    ai_inspection_excute_id: Optional[UUID] = Field(
        ..., description='Ai 提取的特定巡检项目结果的id'
    )


class InspectionRecordConTaskOut(BaseModel):
    model_config = {'from_attributes': True}

    id: UUID = Field(default_factory=uuid4)  # 唯一标识符

    inspection_requirements_id: UUID = Field(..., description=' 巡检要求明细表的唯一标识符')
    status: InspectionResultEnum = Field(
        default=InspectionResultEnum.NORMAL, description='巡检的状态'
    )
    file_id: UUID = Field(description='图片id')

    ai_detection_execute_id: UUID = Field(..., description='AI 执行图片分析的结果')
    ai_inspection_excute_id: UUID = Field(..., description='Ai 提取的特定巡检项目结果的id')
    responsible_person: str = Field(..., description='区域负责人')

    created_by: UUID = Field(..., description='创建者')
    created_at: Optional[datetime] = Field(..., description='创建时间')
    updated_by: Optional[UUID] = Field(..., description='最后更新人时间')
    updated_at: datetime | None = Field(description='更新时间')

    ai_detection_execute: TaskRecordBaseOut = Field(..., description='AI 执行图片分析的结果')
    ai_inspection_excute: TaskRecordBaseOut = Field(
        ..., description='Ai 提取的特定巡检项目结果的id'
    )
    created_by_user: str = Field(..., description='创建者姓名')
    updated_by_user: str = Field(..., description='最后更新人姓名')
