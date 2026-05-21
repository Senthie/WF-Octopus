"""
Author: '浪川' '1214391613@qq.com'
Date: 2026-04-17 10:41:34
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-05-15 17:41:00
FilePath: /api/app/models/ai_inspection/ai_inspection_model.py
Description:Ai 巡检的模型

Copyright (c) 2026 by '浪川' email: '1214391613@qq.com', All Rights Reserved.
"""

from typing import Optional
from uuid import UUID

from sqlmodel import JSON, TEXT, Column, Field, Relationship

from app.enums import InspectionResultEnum
from app.enums.task_enum import TaskStatusEnum
from app.models.auth.user import UserModel
from app.models.base_mixin import (
    AuditMixin,
    BaseModel as MyBaseModel,
    SoftDeleteMixin,
    TimestampMixin,
)
from app.models.task_record import TaskRecordModel


class AiExecuteTaskModel(MyBaseModel, TimestampMixin, SoftDeleteMixin, AuditMixin, table=True):
    """
    执行任务模型

    :param model: 要执行的任务模型
    :param prompt: 要执行的提示语
    :param file_id: file表的id
    :param execute_status: Ai 执行的状态
    :param record: AI结果返回
    """

    __tablename__ = 'ai_execute_task'  # type: ignore
    model: str = Field(description='要执行的任务模型')
    prompt: str = Field(sa_column=Column(TEXT), description='要执行的提示语')
    file_id: UUID = Field(description='图片id')

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

    item_name: str = Field(description='巡检项目名称')
    safety_requirement: str = Field(description='安全要求')


class InspectionRecordModel(MyBaseModel, TimestampMixin, SoftDeleteMixin, AuditMixin, table=True):
    """
    执行记录表

    :param inspection_requirements_id: 巡检要求明细表的唯一标识符
    :param status: 巡检的状态
    :param file_id: 图片id
    :param ai_detection_execute_id: AI 执行图的唯一标识符

    """

    __tablename__ = 'inspection_record'  # type: ignore

    inspection_requirements_id: UUID = Field(description=' 巡检要求明细表的唯一标识符')
    status: InspectionResultEnum = Field(
        default=InspectionResultEnum.NORMAL, description='巡检的状态'
    )
    file_id: UUID = Field(description='图片id')

    ai_detection_execute_id: UUID = Field(description='AI 执行图片分析的结果')
    ai_inspection_excute_id: UUID = Field(description='Ai 提取的特定巡检项目结果的id')

    responsible_person: str = Field(default='', description='区域负责人')

    # ========== 逻辑关联（无物理外键）==========
    ai_detection_execute: Optional[TaskRecordModel] = Relationship(
        sa_relationship_kwargs={
            'primaryjoin': 'InspectionRecordModel.ai_detection_execute_id == TaskRecordModel.id',
            'foreign_keys': '[InspectionRecordModel.ai_detection_execute_id]',
        }
    )
    ai_inspection_excute: Optional[TaskRecordModel] = Relationship(
        sa_relationship_kwargs={
            'primaryjoin': 'InspectionRecordModel.ai_inspection_excute_id == TaskRecordModel.id',
            'foreign_keys': '[InspectionRecordModel.ai_inspection_excute_id]',
        }
    )

    # 假设 created_by 存储的是用户 ID（字符串或 UUID），同样逻辑关联
    created_by_user: Optional[UserModel] = Relationship(
        sa_relationship_kwargs={
            'primaryjoin': 'InspectionRecordModel.created_by == UserModel.id',
            'foreign_keys': '[InspectionRecordModel.created_by]',
        }
    )
    updated_by_user: Optional[UserModel] = Relationship(
        sa_relationship_kwargs={
            'primaryjoin': 'InspectionRecordModel.updated_by == UserModel.id',
            'foreign_keys': '[InspectionRecordModel.updated_by]',
        }
    )
