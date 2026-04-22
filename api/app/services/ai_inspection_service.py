"""
Author: '浪川' '1214391613@qq.com'
Date: 2026-04-20 10:58:16
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-04-22 10:23:19
FilePath: /api/app/services/ai_inspection_service.py
Description:  AI检测服务类，用于处理AI相关的业务逻辑


Copyright (c) 2026 by '浪川' email: '1214391613@qq.com', All Rights Reserved.
"""

import uuid
from uuid import UUID

from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.exceptions import AiInspectionException
from app.enums import CustomResponseCodeEnum
from app.models import InspectionRecordModel
from app.scheams import InspectionRecordin


class AiInspectionService:
    def __init__(self, session: AsyncSession):
        self.session = session

        self.create_by = uuid.UUID('88ca2407-2e66-4f33-a9b1-c99c1f088ca5')

    async def add(self, inD: InspectionRecordin) -> InspectionRecordModel:
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
