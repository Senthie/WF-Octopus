"""
Author: '浪川' '1214391613@qq.com'
Date: 2026-04-22 17:32:02
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-04-28 17:55:51
FilePath: /api/app/services/inspection_requirement_service.py
Description: service层，用于处理巡检要求相关的业务逻辑。

Copyright (c) 2026 by '浪川' email: '1214391613@qq.com', All Rights Reserved.
"""

from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.exceptions import InspectionRequirementException
from app.enums import CustomResponseCodeEnum
from app.models import InspectionRequirementModel
from app.models.auth.user import UserModel
from app.schemas import InspectionRequirementIn, InspectionRequirementOut, PageReq, PageRes


class InspectionRequirementService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(
        self, inD: InspectionRequirementIn, user: UserModel
    ) -> InspectionRequirementModel:
        data = inD.model_dump()  # 或 .dict() 取决于 Pydantic 版本
        data.setdefault('created_by', user.id)  # 例如从上下文中获取
        data.setdefault('updated_by', user.id)

        inspection_record = InspectionRequirementModel(**data)
        self.session.add(inspection_record)
        await self.session.commit()
        return inspection_record

    async def get_by_id(self, id: UUID):
        statement = select(InspectionRequirementModel).where(
            InspectionRequirementModel.id == id, InspectionRequirementModel.is_deleted == False
        )
        record = await self.session.execute(statement)
        record = record.one_or_none()
        if record:
            return record.model_dump()
        else:
            raise InspectionRequirementException(
                CustomResponseCodeEnum.INSPECTION_REQUIREMENT_NOT_FOUND
            )

    async def delete_by_id(self, id: UUID, user: UserModel):
        # 根据 ID 获取的记录，然后软删除
        statement = select(InspectionRequirementModel).where(InspectionRequirementModel.id == id)
        record = await self.session.execute(statement)
        record = record.one_or_none()
        if record:
            record.soft_delete()
            record.updated_by = user.id
            await self.session.commit()

    async def update_by_id(self, id: UUID, inD: InspectionRequirementIn, user: UserModel):
        record = await self.session.get_one(InspectionRequirementModel, id)
        if record:
            # 更新记录的属性
            record.item_name = inD.item_name
            record.safety_requirement = inD.safety_requirement
            record.updated_by = user.id
            record.touch()
            await self.session.commit()
            return record.model_dump()
        else:
            raise InspectionRequirementException(
                CustomResponseCodeEnum.INSPECTION_REQUIREMENT_NOT_FOUND
            )

    async def get_list(self, page_req: PageReq) -> PageRes[InspectionRequirementOut]:
        # Query workflows
        # 计算跳过值
        skip = (page_req.current - 1) * page_req.size
        statement = (
            select(InspectionRequirementModel)
            .where(InspectionRequirementModel.is_deleted != True)  # noqa: E712
            .offset(skip)
            .limit(page_req.size)
        )
        result = await self.session.execute(statement)
        irs = result.scalars().all()
        irs = [InspectionRequirementOut.model_validate(ir) for ir in irs]
        # Count total
        count_statement = (
            select(InspectionRequirementModel).where(InspectionRequirementModel.is_deleted != True)  # noqa: E712
        )
        count_result = await self.session.execute(count_statement)
        total = len(count_result.scalars().all())

        page_res = PageRes.model_validate(page_req.model_dump())
        page_res.records = irs
        page_res.total = total

        return page_res
