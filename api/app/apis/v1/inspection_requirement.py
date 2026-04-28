"""
Author: '浪川' '1214391613@qq.com'
Date: 2026-04-22 17:26:30
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-04-28 17:53:53
FilePath: /api/app/apis/v1/inspection_requirement.py
Description: 巡检要求接口

Copyright (c) 2026 by '浪川' email: '1214391613@qq.com', All Rights Reserved.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.logging import get_logger
from app.core.pg_database import get_session
from app.core.response import ResponseModel, ResponseSchemaModel, response_base
from app.enums.response_code_enum import CustomResponseCodeEnum
from app.middlewares.auth import get_current_user
from app.models.auth.user import UserModel
from app.schemas import InspectionRequirementIn, InspectionRequirementOut
from app.schemas.page_schema import PageReq, PageRes
from app.services import InspectionRequirementService

router = APIRouter(prefix='/inspection-requirement', tags=['inspection requirement v1'])
logger = get_logger(__name__)
# 依赖注入定义
DbSession = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[UserModel, Depends(get_current_user)]


def get_organization_service(session: DbSession) -> InspectionRequirementService:
    """获取企业服务实例"""
    return InspectionRequirementService(session)


InspectionRequirementServiceDep = Annotated[
    InspectionRequirementService, Depends(get_organization_service)
]


@router.post('/', summary='添加检测要求')
async def add(
    inD: InspectionRequirementIn,
    service: InspectionRequirementServiceDep,
    user: CurrentUser,
) -> ResponseModel:
    try:
        res = await service.add(inD, user)
        return response_base.success(
            res=CustomResponseCodeEnum.SUCCESS,
            data=res,
        )

    except Exception as e:
        return response_base.fail(
            res=CustomResponseCodeEnum.INTERNAL_SERVER_ERROR,
            data=f'Failed to extract archive: {str(e)}',
        )


@router.delete('/{id}', summary='删除检测要求')
async def delete_by_id(
    id: UUID,
    service: InspectionRequirementServiceDep,
    user: CurrentUser,
) -> ResponseModel:
    try:
        res = await service.delete_by_id(id, user)
        return response_base.success(
            res=CustomResponseCodeEnum.SUCCESS,
            data=res,
        )

    except Exception as e:
        return response_base.fail(
            res=CustomResponseCodeEnum.INTERNAL_SERVER_ERROR,
            data=f'Failed to extract archive: {str(e)}',
        )


@router.put('/{id}', summary='更新检测要求')
async def update_by_id(
    id: UUID,
    inD: InspectionRequirementIn,
    service: InspectionRequirementServiceDep,
    user: CurrentUser,
) -> ResponseModel:
    try:
        res = await service.update_by_id(id, inD, user)
        return response_base.success(
            res=CustomResponseCodeEnum.SUCCESS,
            data=res,
        )
    except Exception as e:
        return response_base.fail(
            res=CustomResponseCodeEnum.INTERNAL_SERVER_ERROR,
            data=f'Failed to update archive: {str(e)}',
        )


@router.get('/{id}', summary='获取检测要求')
async def get_by_id(id: UUID, service: InspectionRequirementServiceDep) -> ResponseModel:
    try:
        res = await service.get_by_id(id)
        return response_base.success(
            res=CustomResponseCodeEnum.SUCCESS,
            data=res,
        )
    except Exception as e:
        return response_base.fail(
            res=CustomResponseCodeEnum.INTERNAL_SERVER_ERROR,
            data=f'Failed to get archive: {str(e)}',
        )


@router.post('/list')
async def list_workflows(
    page_req: PageReq,
    service: InspectionRequirementServiceDep,
) -> ResponseSchemaModel[PageRes[InspectionRequirementOut]]:
    """
    List all workflows in the specified workspace.

    Args:
        workspace_id: ID of the workspace
        current_user: Current authenticated user
        session: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of workflows and total count
    """

    res = await service.get_list(page_req=page_req)
    return response_base.success(data=res)  # type: ignore
