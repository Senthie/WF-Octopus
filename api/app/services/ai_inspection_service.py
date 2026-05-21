"""
Author: '浪川' '1214391613@qq.com'
Date: 2026-04-20 10:58:16
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-05-21 17:10:19
FilePath: /api/app/services/ai_inspection_service.py
Description:  AI检测服务类，用于处理AI相关的业务逻辑


Copyright (c) 2026 by '浪川' email: '1214391613@qq.com', All Rights Reserved.
"""

from typing import Dict, Optional, Tuple
import uuid
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.exceptions import AiInspectionException, InspectionRequirementException
from app.enums import CustomResponseCodeEnum
from app.models import InspectionRecordModel, InspectionRequirementModel
from app.models.auth.user import UserModel
from app.models.task_record import TaskRecordModel
from app.schemas import InspectionRecordIn
from app.schemas.ai_inspection_schema import (
    InspectionRecordConTaskOut,
    InspectionRecordOut,
    InspectionRecordUpdateIn,
)
from app.schemas.inspection_requirement_schema import InspectionRequirementOut
from app.schemas.page_schema import PageReq, PageRes
from app.schemas.task_schema import TaskRecordBaseOut


class AiInspectionService:
    def __init__(self, session: AsyncSession):
        self.session = session

        self.create_by = uuid.UUID('88ca2407-2e66-4f33-a9b1-c99c1f088ca5')

    async def add(
        self,
        inD: InspectionRecordIn,
        user: UserModel,
        ai_detection_execute_id: Optional[UUID] = None,
        ai_inspection_excute_id: Optional[UUID] = None,
    ) -> Tuple[InspectionRecordOut, InspectionRequirementOut]:
        """

        :celery_task_id: str 这里返回的是 pg sql 里表 id 不是 celery 的真正任务ID
        """
        # 根据巡检要求明细表，获取要求内容
        ir = await self.session.get(InspectionRequirementModel, inD.inspection_requirements_id)
        if ir:
            ir_schema = InspectionRequirementOut.model_validate(ir)
        else:
            raise InspectionRequirementException(
                CustomResponseCodeEnum.INSPECTION_REQUIREMENT_NOT_FOUND
            )
        user_id = user.id
        try:
            data = inD.model_dump()  # 或 .dict() 取决于 Pydantic 版本
            data.setdefault('created_by', user_id)  # 例如从上下文中获取
            data.setdefault('ai_detection_execute_id', ai_detection_execute_id)  # 或生成 UUID
            data.setdefault('ai_inspection_excute_id', ai_inspection_excute_id)
            data.setdefault('updated_by', user_id)

            inspection_record = InspectionRecordModel(**data)
            self.session.add(inspection_record)
            await self.session.commit()
        except Exception:
            await self.session.rollback()

        return InspectionRecordOut.model_validate(inspection_record), ir_schema

    async def get_by_id(self, id: UUID) -> InspectionRecordOut:
        record = await self.session.get(InspectionRecordModel, id)
        if not record:
            raise AiInspectionException(CustomResponseCodeEnum.INSPECTION_RECORD_NOT_FOUND)

        return InspectionRecordOut.model_validate(record)

    async def delete_by_id(self, id: UUID, user: UserModel):
        # 根据 ID 获取的记录，然后软删除
        record = await self.session.get_one(InspectionRecordModel, id)
        if record:
            record.soft_delete()
            record.updated_by = user.id
            await self.session.commit()

    async def update_by_id(self, id: UUID, inD: InspectionRecordUpdateIn, user: UserModel):
        record = await self.session.get_one(InspectionRecordModel, id)

        if record:
            # 更新记录的属性
            record.status = inD.status
            record.responsible_person = inD.responsible_person

            record.updated_by = user.id
            record.touch()
            await self.session.commit()

        else:
            raise AiInspectionException(CustomResponseCodeEnum.INSPECTION_REQUIREMENT_NOT_FOUND)

        ai_detection_execute = await self.session.get_one(
            TaskRecordModel, record.ai_detection_execute_id
        )
        ai_inspection_excute = await self.session.get_one(
            TaskRecordModel, record.ai_inspection_excute_id
        )
        ai_detection_execute.result = {'response': inD.ai_detection_execute_result}
        ai_detection_execute.touch()
        ai_detection_execute.updated_by = user.id

        ai_inspection_excute.result = {'result': inD.ai_inspection_excute_result}
        ai_inspection_excute.touch()
        ai_inspection_excute.updated_by = user.id

        await self.session.commit()
        return InspectionRecordOut.model_validate(record)

    async def get_list(self, page_req: PageReq) -> PageRes[InspectionRecordConTaskOut]:
        # ---------- 数据查询（预加载关联，避免 N+1） ----------
        offset = (page_req.current - 1) * page_req.size
        stmt = (
            select(InspectionRecordModel)
            .where(InspectionRecordModel.is_deleted != True)
            .options(
                selectinload(InspectionRecordModel.ai_detection_execute),
                selectinload(InspectionRecordModel.ai_inspection_excute),
                selectinload(InspectionRecordModel.created_by_user),
            )
            .offset(offset)
            .limit(page_req.size)
            .order_by(InspectionRecordModel.created_at.desc())  # 建议加排序，保证分页稳定
        )
        result = await self.session.execute(stmt)
        records = result.scalars().all()

        # ---------- 转换为输出对象 ----------
        out_list = [self._to_inspection_record_con_task_out(r) for r in records]

        # ---------- 高性能计数 ----------
        count_stmt = (
            select(func.count())
            .select_from(InspectionRecordModel)
            .where(InspectionRecordModel.is_deleted != True)
        )
        total = await self.session.scalar(count_stmt)

        # ---------- 构建分页响应 ----------
        page_res = PageRes.model_validate(page_req.model_dump())
        page_res.records = out_list
        page_res.total = total if total else 0
        return page_res

    async def patch_data_by_id(self, id: UUID, data: Dict, user: UserModel):
        record = await self.session.get_one(InspectionRecordModel, id)
        if record:
            # 更新记录的属性
            for key, value in data.items():
                setattr(record, key, value)

            record.updated_by = user.id
            record.touch()
            await self.session.commit()
            return InspectionRecordOut.model_validate(record)
        else:
            raise AiInspectionException(CustomResponseCodeEnum.INSPECTION_REQUIREMENT_NOT_FOUND)

    def _to_inspection_record_con_task_out(
        self,
        record: InspectionRecordModel,
    ) -> InspectionRecordConTaskOut:
        """将 ORM 对象手动映射为输出 Schema，正确处理关联对象"""

        try:
            ai_detection_execute = TaskRecordBaseOut.model_validate(record.ai_detection_execute)
            ai_inspection_excute = TaskRecordBaseOut.model_validate(record.ai_inspection_excute)

            return InspectionRecordConTaskOut(
                id=record.id,
                inspection_requirements_id=record.inspection_requirements_id,
                status=record.status,
                file_id=record.file_id,
                ai_detection_execute_id=record.ai_detection_execute_id,
                ai_inspection_excute_id=record.ai_inspection_excute_id,
                # 关联的 TaskModel 转换为 TaskRecordBaseOut（如果关联存在）
                ai_detection_execute=ai_detection_execute,
                ai_inspection_excute=ai_inspection_excute,
                responsible_person=record.responsible_person,
                # 从用户关联中取 username，若不存在则给默认值
                created_by=record.created_by,
                created_at=record.created_at,
                updated_by=record.updated_by,  # AuditMixin 中直接存的 UUID
                updated_at=record.updated_at,
                created_by_user=record.created_by_user.name if record.created_by_user else '',
                updated_by_user=record.updated_by_user.name if record.updated_by_user else '',
            )
        except Exception as e:
            raise AiInspectionException(
                CustomResponseCodeEnum.INTERNAL_SERVER_ERROR, message=str(e)
            ) from e
