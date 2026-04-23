"""
Author: '浪川' '1214391613@qq.com'
Date: 2026-04-20 10:58:16
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-04-23 14:51:19
FilePath: /api/app/services/ai_inspection_service.py
Description:  AI检测服务类，用于处理AI相关的业务逻辑


Copyright (c) 2026 by '浪川' email: '1214391613@qq.com', All Rights Reserved.
"""

import uuid
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.exceptions import AiInspectionException
from app.enums import CustomResponseCodeEnum
from app.models import InspectionRecordModel
from app.scheams import InspectionRecordIn
from app.scheams.ai_inspection_scheam import InspectionRecordOut
from app.scheams.page_schemas import PageReq, PageRes


class AiInspectionService:
    def __init__(self, session: AsyncSession):
        self.session = session

        self.create_by = uuid.UUID('88ca2407-2e66-4f33-a9b1-c99c1f088ca5')

    async def add(self, inD: InspectionRecordIn) -> InspectionRecordModel:
        data = inD.model_dump()  # 或 .dict() 取决于 Pydantic 版本
        data.setdefault('created_by', self.create_by)  # 例如从上下文中获取
        data.setdefault('ai_detection_execute_id', None)  # 或生成 UUID
        data.setdefault('ai_inspection_excute_id', None)
        data.setdefault('updated_by', self.create_by)

        inspection_record = InspectionRecordModel(**data)
        self.session.add(inspection_record)
        await self.session.commit()
        return inspection_record

    async def get_by_id(self, id: UUID):
        record = await self.session.get(InspectionRecordModel, id)
        if record:
            return record.model_dump()
        else:
            raise AiInspectionException(CustomResponseCodeEnum.INSPECTION_RECORD_NOT_FOUND)

    async def delete_by_id(self, id: UUID):
        # 根据 ID 获取的记录，然后软删除
        record = await self.session.get_one(InspectionRecordModel, id)
        if record:
            record.soft_delete()
            record.updated_by = self.create_by
            await self.session.commit()

    async def update_by_id(self, id: UUID, inD: InspectionRecordIn):
        record = await self.session.get_one(InspectionRecordModel, id)
        if record:
            # 更新记录的属性
            for key, value in inD.model_dump(exclude_unset=True).items():
                setattr(record, key, value)

            record.updated_by = self.create_by
            record.touch()
            await self.session.commit()
            return record.model_dump()
        else:
            raise AiInspectionException(CustomResponseCodeEnum.INSPECTION_REQUIREMENT_NOT_FOUND)

    async def get_list(self, page_req: PageReq) -> PageRes[InspectionRecordOut]:
        # Query workflows
        # 计算跳过值
        skip = (page_req.current - 1) * page_req.size
        statement = (
            select(InspectionRecordModel)
            .where(InspectionRecordModel.is_deleted != True)  # noqa: E712
            .offset(skip)
            .limit(page_req.size)
        )
        result = await self.session.execute(statement)
        irs = result.scalars().all()
        irs = [InspectionRecordOut.model_validate(ir) for ir in irs]
        # Count total
        count_statement = (
            select(InspectionRecordModel).where(InspectionRecordModel.is_deleted != True)  # noqa: E712
        )
        count_result = await self.session.execute(count_statement)
        total = len(count_result.scalars().all())

        page_res = PageRes.model_validate(page_req.model_dump())
        page_res.records = irs
        page_res.total = total

        return page_res
