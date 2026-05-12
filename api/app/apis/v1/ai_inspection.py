"""
Author: '浪川' '1214391613@qq.com'
Date: 2026-04-16 16:33:10
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-05-12 17:49:54
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
from app.middlewares.auth import get_current_user
from app.models.auth.user import UserModel
from app.schemas import InspectionRecordIn
from app.schemas.ai_inspection_schema import InspectionRecordOut
from app.schemas.page_schema import PageReq, PageRes
from app.services import AiInspectionService, CeleryTaskRecordService

# Use Dramatiq async actor instead of Celery
from app.tasks.inspection_dramatiq import ai_inspection_task_async

router = APIRouter(prefix='/ai-inspection', tags=['ai inspection v1'])
logger = get_logger(__name__)
# 依赖注入定义
DbSession = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[UserModel, Depends(get_current_user)]


def get_organization_service(session: DbSession) -> AiInspectionService:
    """获取企业服务实例"""
    return AiInspectionService(session)


AiInspectionServiceDep = Annotated[AiInspectionService, Depends(get_organization_service)]


def get_celery_db_help(db: DbSession) -> CeleryTaskRecordService:
    """获取认证服务实例"""
    return CeleryTaskRecordService(db)


CeleryServiceDep = Annotated[CeleryTaskRecordService, Depends(get_celery_db_help)]


@router.post('/', summary='添加检测的拍照记录')
async def add(
    inD: InspectionRecordIn,
    user: CurrentUser,
    service: AiInspectionServiceDep,
    celery_service: CeleryServiceDep,
) -> ResponseModel:
    """
    接收一个检测的拍照记录
    """

    try:
        # 优先创建一个空的识别数据
        celery_record = await celery_service.create_task_record(
            task_id='',
            task_name='ai_inspection_task',
            args=[],
            kwargs={},
        )
        # 获取数据
        record_out, inspection_requirement_out = await service.add(inD, user, celery_record.id)
        # Dispatch to Dramatiq async actor
        ai_inspection_task_async.send(
            record_out.model_dump_json(),
            inspection_requirement_out.model_dump_json(),
            str(celery_record.id),
        )
        return response_base.success(
            res=CustomResponseCodeEnum.SUCCESS,
            data=record_out,
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
async def delete_by_id(
    id: UUID, user: CurrentUser, service: AiInspectionServiceDep
) -> ResponseModel:
    """ """

    try:
        await service.delete_by_id(id, user=user)
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
    id: UUID, inD: InspectionRecordIn, user: CurrentUser, service: AiInspectionServiceDep
) -> ResponseModel:
    try:
        res = await service.update_by_id(id, inD, user=user)
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
