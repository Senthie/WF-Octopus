"""
Author: '浪川' '1214391613@qq.com'
Date: 2026-04-07 10:50:57
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-05-13 15:31:58
FilePath: /api/app/main.py
Description:

Copyright (c) 2026 by '浪川' email: '1214391613@qq.com', All Rights Reserved.
"""

# Create FastAPI application
from contextlib import asynccontextmanager
import logging
from logging.handlers import TimedRotatingFileHandler
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles

from app.apis.v1 import router as v1_router
from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.core.mongodb import mongodb_client
from app.core.pg_database import close_db, init_db
from app.core.redis import redis_client
from app.middlewares.auth import AuthMiddleware

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')
# Configure logging
configure_logging()
logger = get_logger(__name__)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler = TimedRotatingFileHandler(filename='logs/app.log', when='D', backupCount=7)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup
    logger.info('Starting application', app_name=settings.app_name)

    try:
        # Initialize database
        await init_db()
        logger.info('Database initialized')

        # Connect to MongoDB
        await mongodb_client.connect()
        logger.info('MongoDB connected')

        # Connect to Redis
        await redis_client.connect()
        logger.info('Redis connected')

    except Exception as e:
        logger.error('Failed to initialize application', error=str(e))
        raise

    yield

    # Shutdown
    logger.info('Shutting down application')

    try:
        await close_db()
        await mongodb_client.close()
        # await redis_client.close()
        logger.info('All connections closed')
    except Exception as e:
        logger.error('Error during shutdown', error=str(e))


app = FastAPI(
    title='WF-Octopus API',
    version='0.1.0',
    description='Low-code platform backend with workflow orchestration and AI integration',
    docs_url=None,
    redoc_url=None,
    openapi_url='/openapi.json',
    lifespan=lifespan,
)

# 2. 将静态文件目录挂载到 '/resources' 路径
app.mount('/resources', StaticFiles(directory='app/resources'), name='resources')


@app.get('/')
def get_root():
    return {'message': 'Welcome to the WF-Octopus API'}


# 3. 手动定义一个 /docs 路由，使用本地静态文件
@app.get('/docs', include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url='/openapi.json',  # 使用硬编码的 openapi_url
        title=app.title + ' - Swagger UI',
        # 使用本地静态文件
        swagger_js_url='/resources/static/docs-ui/swagger-ui-bundle.js',
        swagger_css_url='/resources/static/docs-ui/swagger-ui.css',
    )


app.include_router(v1_router)
# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)
# 在 CORS 中间件之后添加认证中间件
app.add_middleware(AuthMiddleware)
