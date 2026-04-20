"""
Author: '浪川' '1214391613@qq.com'
Date: 2026-04-20 15:06:01
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-04-20 16:27:42
FilePath: /api/alembic/env.py
Description: Alembic环境初始化


Copyright (c) 2026 by '浪川' email: '1214391613@qq.com', All Rights Reserved.
"""

from logging.config import fileConfig
import os
import sys

import sqlalchemy as sa
from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel
from sqlmodel.sql.sqltypes import AutoString

from alembic import context

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Load environment variables from .env file
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    # dotenv not available, skip loading .env file
    pass


# Import all models to ensure they are registered with SQLModel

from app.models import (  # noqa: F401
    AiExecuteTaskModel,
    InspectionRecordModel,
    InspectionRequirementModel,
)

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = SQLModel.metadata


def render_item(obj_type, obj, autogen_context):
    """将 SQLModel 的 AutoString 渲染为标准 sa.String()，避免迁移文件依赖 sqlmodel。"""
    if obj_type == 'type' and isinstance(obj, AutoString):
        return 'sa.String()'
    return False


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_database_url() -> str:
    """Get database URL from environment variables or config."""
    # Try to get from environment first
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        # Convert async URL to sync for Alembic
        if 'postgresql+asyncpg://' in database_url:
            database_url = database_url.replace('postgresql+asyncpg://', 'postgresql://')
        return database_url

    # Fallback to config file
    config_url = config.get_main_option('sqlalchemy.url')
    if config_url:
        return config_url

    # Default fallback for development (sync driver for Alembic)
    return 'postgresql://postgres:postgres@localhost:5432/lowcode_platform'


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={'paramstyle': 'named'},
        render_item=render_item,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    # Override the sqlalchemy.url with environment variable if available
    configuration = config.get_section(config.config_ini_section, {})
    database_url = get_database_url()
    configuration['sqlalchemy.url'] = database_url

    connectable = engine_from_config(
        configuration,
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, render_item=render_item)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
