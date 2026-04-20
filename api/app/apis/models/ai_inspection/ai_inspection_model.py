"""
Author: '浪川' '1214391613@qq.com'
Date: 2026-04-17 10:41:34
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-04-20 10:35:37
FilePath: /api/app/apis/models/ai_inspection/ai_inspection_model.py
Description:Ai 巡检的模型

Copyright (c) 2026 by '浪川' email: '1214391613@qq.com', All Rights Reserved.
"""

from uuid import UUID, uuid4

from sqlmodel import JSON, TEXT, Column, Field

from app.apis.models.base_mixin import (
    AuditMixin,
    BaseModel as MyBaseModel,
    SoftDeleteMixin,
    TimestampMixin,
)
from app.enums.task_enum import TaskStatusEnum


class AiExecuteTaskModel(MyBaseModel, TimestampMixin, SoftDeleteMixin, AuditMixin, table=True):
    """
    执行任务模型

    :param model: 要执行的任务模型
    :param prompt: 要执行的提示语
    :param image_gridfs_id: 图片id
    :param execute_status: Ai 执行的状态
    :param record: AI结果返回
    """

    __tablename__ = 'ai_execute_task'  # type: ignore
    model: str = Field(..., description='要执行的任务模型')
    prompt: str = Field(..., sa_column=Column(TEXT), description='要执行的提示语')
    image_gridfs_id: str = Field(description='图片id')

    execute_status: TaskStatusEnum = Field(
        default=TaskStatusEnum.PENDING, description='Ai 执行的状态'
    )
    record: dict = Field(default={}, sa_column=Column(JSON), description='AI结果返回')


class InspectionRequirementModel(
    MyBaseModel, TimestampMixin, SoftDeleteMixin, AuditMixin, table=True
):
    """
    巡检要求明细表

    :param item_name: 巡检项目名称
    :param safety_requirement: 安全要求

    """

    __tablename__ = 'inspection_requirement'  # type: ignore

    item_name: str = Field(..., description='巡检项目名称')
    safety_requirement: str = Field(..., description='安全要求')


class InspectionRecordModel(MyBaseModel, TimestampMixin, SoftDeleteMixin, AuditMixin, table=True):
    """
    执行记录表
    :param inspection_requirements_id: 巡检要求明细表的唯一标识符
    :param status: 巡检的状态
    :param image_gridfs_id: 图片id
    :param ai_detection_execute_id: AI 执行图的唯一标识符

    """

    __tablename__ = 'inspection_record'  # type: ignore

    id: UUID = Field(default_factory=uuid4)  # 唯一标识符

    inspection_requirements_id: UUID = Field(..., description=' 巡检要求明细表的唯一标识符')
    status: str = Field(..., description='巡检的状态')
    image_gridfs_id: str = Field(description='图片id')

    ai_detection_execute_id: UUID = Field(..., description='AI 执行图片分析的结果')
    ai_inspection_excute_id: UUID = Field(..., description='Ai 提取的特定巡检项目结果的id')

    responsible_person: str = Field(..., description='区域负责人')
