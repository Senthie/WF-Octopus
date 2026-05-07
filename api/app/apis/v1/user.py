"""
Author: '浪川' '1214391613@qq.com'
Date: 2026-04-27 17:27:26
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-05-07 12:10:30
FilePath: /api/app/apis/v1/user.py
Description: 认证相关API端点

Copyright (c) 2026 by '浪川' email: '1214391613@qq.com', All Rights Reserved.
"""

from typing import Annotated, Dict, List
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.exceptions import AuthException
from app.core.pg_database import get_session
from app.core.redis import RedisClient, get_redis
from app.core.response import ResponseModel, ResponseSchemaModel, response_base
from app.enums.response_code_enum import CustomResponseCodeEnum
from app.services import UserService

router = APIRouter(prefix='/user', tags=['v1 user api'])

# 依赖注入定义
DbSession = Annotated[AsyncSession, Depends(get_session)]
Redis = Annotated[RedisClient, Depends(get_redis)]


def get_user_service(db: DbSession, redis: Redis) -> UserService:
    """获取认证服务实例"""
    return UserService(db, redis)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]


@router.post(
    '/usernames',
    summary='根据ID获取用户名',
)
async def get_usernames_by_ids(
    ids: List[UUID],
    auth_service: UserServiceDep,
) -> ResponseSchemaModel[Dict[UUID, str]] | ResponseModel:
    """
    根据 IDS 获取用户名
    """
    try:
        response = await auth_service.get_usernames_by_ids(ids)
        return response
    except AuthException as e:
        # 返回业务异常的响应格式
        return response_base.fail(
            res=e.response_code,
            data=f'Failed to create workflow: {str(e)}',
        )
    except Exception as e:
        # 返回未知异常的响应格式
        return response_base.fail(
            res=CustomResponseCodeEnum.UNKNOWN_ERROR,
            data=str(e),
        )
