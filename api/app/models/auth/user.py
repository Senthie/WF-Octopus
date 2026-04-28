"""
Author: '浪川' '1214391613@qq.com'
Date: 2026-04-27 12:26:08
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-04-27 16:20:24
FilePath: /api/app/models/auth/user.py
Description: 用户表

Copyright (c) 2026 by '浪川' email: '1214391613@qq.com', All Rights Reserved.
"""

from typing import Optional

from sqlmodel import Field

from app.models.base_mixin import BaseModel, SoftDeleteMixin, TimestampMixin


class UserModel(BaseModel, TimestampMixin, SoftDeleteMixin, table=True):
    """用户表 - 系统用户账户。

    存储系统用户的基本信息和认证凭证。
    用户可以属于多个团队，通过 TeamMember 表建立关联。
    实现了软删除的字段设计

    继承
        :param id: 用户唯一标识符（UUID）
        :param created_at: 创建时间
        :param updated_at: 最后更新时间
        :param deleted_at: Optional[datetime] = Field(default=None)
        :param is_deleted: bool = Field(default=False)

        :param name: 用户姓名
        :param email: 用户邮箱（唯一，用于登录）
        :param password_hash: 密码哈希值
        :param avatar_url: 头像URL
    """

    __tablename__ = 'users'  # type: ignore # noqa: W291
    name: str = Field(max_length=255)
    email: str = Field(unique=True, index=True, max_length=255)
    password_hash: str = Field(max_length=255)
    avatar_url: Optional[str] = Field(default=None, max_length=500)
