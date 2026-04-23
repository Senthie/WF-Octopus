"""
Author: '浪川' '1214391613@qq.com'
Date: 2026-04-23 12:04:07
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-04-23 12:05:22
FilePath: /api/app/scheams/page_schemas.py
Description: 自定义响应码枚举类，用于表示不同的响应状态码。<|system_separator_istruction_repository_level|>


Copyright (c) 2026 by '浪川' email: '1214391613@qq.com', All Rights Reserved.
"""

from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar('T')


class PageReq(BaseModel):
    """
    Request list by page create a page list schema
    """

    total: int = Field(default=0, description='查询列表总记录数')
    size: int = Field(default=10, description='每页显示条数，默认 10')
    current: int = Field(default=1, description='当前页')
    orders: Optional[List[str]] = Field(default=[], description='排序字段信息')
    maxLimit: Optional[int] = Field(default=None, description='限制每页最大条数，默认无限制')


class PageRes(BaseModel, Generic[T]):
    """
    response page list
    """

    records: List[T] = Field(default=[], description='记录列表')
    total: int = Field(default=0, description='查询列表总记录数')
    size: int = Field(default=10, description='每页显示条数，默认 10')
    current: int = Field(default=1, description='当前页')
    orders: Optional[List[str]] = Field(default=[], description='排序字段信息')
    maxLimit: Optional[int] = Field(default=None, description='限制每页最大条数，默认无限制')
