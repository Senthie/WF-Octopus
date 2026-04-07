"""
Author: '浪川' '1214391613@qq.com'
Date: 2026-04-03 12:15:48
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-04-07 10:49:24
FilePath: /api/app/apis/v1/__init__.py
Description: 模块初始化文件，导入v1版本的API接口

Copyright (c) 2026 by '浪川' email: '1214391613@qq.com', All Rights Reserved.
"""

from fastapi import APIRouter

from app.apis.v1 import zip as zip_api

# router实例，所有v1版本的API接口都将注册到这个router上
router = APIRouter(
    prefix="/api/v1",
)

router.include_router(zip_api.router)
