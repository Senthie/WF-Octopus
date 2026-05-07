"""
Author: '浪川' '1214391613@qq.com'
Date: 2026-05-07 11:25:54
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-05-07 11:59:55
FilePath: /api/app/services/user_service.py
Description:

Copyright (c) 2026 by '浪川' email: '1214391613@qq.com', All Rights Reserved.
"""

from typing import Dict, List
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.redis import RedisClient
from app.core.response import ResponseModel, response_base
from app.models.auth import UserModel


class UserService:
    """Service for handling authentication operations."""

    def __init__(self, db: AsyncSession, redis: RedisClient):
        """
        Initialize UserService.

        Args:
            db: Async database session
            redis: Redis client for token management
        """
        self.db = db
        self.redis = redis

    async def get_usernames_by_ids(self, ids: List[UUID]) -> ResponseModel:
        """
        Get usernames by user ids.

        Args:
            ids: List of user UUIDs

        Returns:
            ResponseModel with data as dict mapping user_id (str) to username
        """
        # 对ids 进行去重
        set_ids = [str(id) for id in ids]
        set_ids = set(set_ids)
        if not ids:
            return response_base.success(data={})

        # 批量查询用户 id 和 username
        stmt = select(UserModel.id, UserModel.name).where(UserModel.id.in_(set_ids))
        result = await self.db.execute(stmt)
        rows = result.all()

        # 构建 {user_id: username} 字典
        usernames: Dict[str, str] = {str(row.id): row.name for row in rows}
        # 没查询到的就设置为 未知
        for id in set_ids:
            if not usernames.get(id, None):
                usernames[id] = '未知'
        return response_base.success(data=usernames)
