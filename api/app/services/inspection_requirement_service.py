import uuid

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import InspectionRequirementModel
from app.scheams import InspectionRequirementIn


class InspectionRequirementService:
    def __init__(self, session: AsyncSession):
        self.session = session

        self.create_by = uuid.UUID('88ca2407-2e66-4f33-a9b1-c99c1f088ca5')

    async def add(self, inD: InspectionRequirementIn) -> InspectionRequirementModel:
        data = inD.model_dump()  # 或 .dict() 取决于 Pydantic 版本
        # TODO 需要从上下文获取，而不是写死
        data.setdefault('created_by', self.create_by)  # 例如从上下文中获取
        data.setdefault('updated_by', self.create_by)

        inspection_record = InspectionRequirementModel(**data)
        self.session.add(inspection_record)
        await self.session.commit()
        return inspection_record
