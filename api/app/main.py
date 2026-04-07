"""
Author: '浪川' '1214391613@qq.com'
Date: 2026-04-07 10:50:57
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-04-07 10:55:48
FilePath: /api/app/main.py
Description:

Copyright (c) 2026 by '浪川' email: '1214391613@qq.com', All Rights Reserved.
"""

# Create FastAPI application
from fastapi import FastAPI

from app.apis.v1 import router as v1_router

app = FastAPI(
    title="WF-Octopus API",
    version="0.1.0",
    description="Low-code platform backend with workflow orchestration and AI integration",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.include_router(v1_router)
