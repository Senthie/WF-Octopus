"""
Author: '浪川' '1214391613@qq.com'
Date: 2026-04-16 16:33:10
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-04-23 14:18:14
FilePath: /api/app/apis/v1/ai_inspection.py
Description: 巡检接口点

·
Copyright (c) 2026 by '浪川' email: '1214391613@qq.com', All Rights Reserved.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.exceptions import AiInspectionException
from app.core.logging import get_logger
from app.core.pg_database import get_session
from app.core.response import ResponseModel, ResponseSchemaModel, response_base
from app.enums.response_code_enum import CustomResponseCodeEnum
from app.scheams import InspectionRecordIn
from app.scheams.ai_inspection_scheam import InspectionRecordOut
from app.scheams.page_schemas import PageReq, PageRes
from app.services import AiInspectionService

router = APIRouter(prefix='/ai-inspection', tags=['ai inspection v1'])
logger = get_logger(__name__)
# 依赖注入定义
DbSession = Annotated[AsyncSession, Depends(get_session)]


def get_organization_service(session: DbSession) -> AiInspectionService:
    """获取企业服务实例"""
    return AiInspectionService(session)


AiInspectionServiceDep = Annotated[AiInspectionService, Depends(get_organization_service)]


@router.post('/', summary='添加检测的拍照记录')
async def add(inD: InspectionRecordIn, service: AiInspectionServiceDep) -> ResponseModel:
    """
    接收一个检测的拍照记录
    """

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


@router.get('/', summary='根据ID 获取检测的拍照记录')
async def get_by_id(id: UUID, service: AiInspectionServiceDep) -> ResponseModel:
    """
    接收一个检测的拍照记录
    """

    try:
        res = await service.get_by_id(id)
        return response_base.success(
            res=CustomResponseCodeEnum.SUCCESS,
            data=res,
        )
    except AiInspectionException as e:
        return response_base.fail(
            res=e.response_code,
            data=f'{str(e)}',
        )
    except Exception as e:
        return response_base.fail(
            res=CustomResponseCodeEnum.INTERNAL_SERVER_ERROR,
            data=f'Failed to extract archive: {str(e)}',
        )


@router.delete('/', summary='根据ID 删除检测的拍照记录')
async def delete_by_id(id: UUID, service: AiInspectionServiceDep) -> ResponseModel:
    """ """

    try:
        await service.delete_by_id(id)
        return response_base.success(
            res=CustomResponseCodeEnum.SUCCESS,
        )
    except AiInspectionException as e:
        return response_base.fail(
            res=e.response_code,
            data=f'{str(e)}',
        )
    except Exception as e:
        return response_base.fail(
            res=CustomResponseCodeEnum.INTERNAL_SERVER_ERROR,
            data=f'Failed to extract archive: {str(e)}',
        )


@router.put('/{id}', summary='更新检测的拍照记录')
async def update_by_id(
    id: UUID, inD: InspectionRecordIn, service: AiInspectionServiceDep
) -> ResponseModel:
    try:
        res = await service.update_by_id(id, inD)
        return response_base.success(
            res=CustomResponseCodeEnum.SUCCESS,
            data=res,
        )
    except Exception as e:
        return response_base.fail(
            res=CustomResponseCodeEnum.INTERNAL_SERVER_ERROR,
            data=f'Failed to update archive: {str(e)}',
        )


@router.post('/list')
async def list_(
    page_req: PageReq,
    service: AiInspectionServiceDep,
) -> ResponseSchemaModel[PageRes[InspectionRecordOut]]:
    """
    获取巡检记录列表

    """

    res = await service.get_list(page_req=page_req)
    return response_base.success(data=res)  # type: ignore
