"""
Author: '浪川' '1214391613@qq.com'
Date: 2026-04-20 10:58:16
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-04-21 15:47:24
FilePath: /api/app/services/ai_inspection_service.py
Description:  AI检测服务类，用于处理AI相关的业务逻辑


Copyright (c) 2026 by '浪川' email: '1214391613@qq.com', All Rights Reserved.
"""

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import InspectionRecordModel
from app.scheams import InspectionRecordin


class AiInspectionService:
    def __init__(self, session: AsyncSession):
        self.session = session

        self.create_by = '88ca2407-2e66-4f33-a9b1-c99c1f088ca5'

    async def add(self, inD: InspectionRecordin):
        data = inD.model_dump()  # 或 .dict() 取决于 Pydantic 版本
        data.setdefault('created_by', self.create_by)  # 例如从上下文中获取
        data.setdefault('ai_detection_execute_id', None)  # 或生成 UUID
        data.setdefault('ai_inspection_excute_id', None)

        inspection_record = InspectionRecordModel(**data)
        self.session.add(inspection_record)
        await self.session.commit()
        return inspection_record
