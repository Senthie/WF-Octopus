"""
Author: '浪川' '1214391613@qq.com'
Date: 2026-04-07 10:50:57
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-04-21 11:43:19
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

from app.apis.v1 import router as v1_router
from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.core.mongodb import mongodb_client
from app.core.pg_database import close_db, init_db

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
        # await redis_client.connect()
        # logger.info('Redis connected')

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
    docs_url='/docs',
    redoc_url='/redoc',
    openapi_url='/openapi.json',
    lifespan=lifespan,
)

app.include_router(v1_router)
