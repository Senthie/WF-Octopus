"""
Author: '浪川' '1214391613@qq.com'
Date: 2026-04-03 12:15:48
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-05-09 15:23:46
FilePath: /api/app/apis/v1/__init__.py
Description: 模块初始化文件，导入v1版本的API接口

Copyright (c) 2026 by '浪川' email: '1214391613@qq.com', All Rights Reserved.
"""

from fastapi import APIRouter

from app.apis.v1 import (
    ai_inspection as ai_inspection_api,
    auth as auth_api,
    celery as celery_api,
    file as file_api,
    inspection_requirement as inspection_requirement_api,
    pdf as pdf_api,
    user as user_api,
    zip as zip_api,
)

# router实例，所有v1版本的API接口都将注册到这个router上
router = APIRouter(
    prefix='/api/v1',
)

router.include_router(zip_api.router)
router.include_router(file_api.router)

router.include_router(pdf_api.router)

router.include_router(ai_inspection_api.router)
router.include_router(inspection_requirement_api.router)
router.include_router(auth_api.router)
router.include_router(user_api.router)

router.include_router(celery_api.router)
