"""
Author: '浪川' '1214391613@qq.com'
Date: 2026-04-22 17:26:30
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-04-22 17:41:59
FilePath: /api/app/apis/v1/inspection_requirement.py
Description: 巡检要求接口

Copyright (c) 2026 by '浪川' email: '1214391613@qq.com', All Rights Reserved.
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.logging import get_logger
from app.core.pg_database import get_session
from app.core.response import ResponseModel, response_base
from app.enums.response_code_enum import CustomResponseCodeEnum
from app.scheams import InspectionRequirementIn
from app.services import InspectionRequirementService

router = APIRouter(prefix='/inspection-requirement', tags=['inspection requirement v1'])
logger = get_logger(__name__)
# 依赖注入定义
DbSession = Annotated[AsyncSession, Depends(get_session)]


def get_organization_service(session: DbSession) -> InspectionRequirementService:
    """获取企业服务实例"""
    return InspectionRequirementService(session)


InspectionRequirementServiceDep = Annotated[
    InspectionRequirementService, Depends(get_organization_service)
]


@router.post('/', summary='添加检测要求')
async def add(inD: InspectionRequirementIn, service: InspectionRequirementServiceDep) -> ResponseModel:
    try:
        res = await service.add(inD)
        return response_base.success(
            res=CustomResponseCodeEnum.SUCCESS,
            data=res,
        )

    except Exception as e:
        return response_base.fail(
            res=CustomResponseCodeEnum.INTERNAL_SERVER_ERROR,
            data=f'Failed to extract archive: {str(e)}',
        )
