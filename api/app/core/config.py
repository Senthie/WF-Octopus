"""
Author: kk123047 3254834740@qq.com
Date: 2025-12-09 18:00:00
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-04-21 11:46:25
FilePath: /api/app/core/config.py
Description: 应用配置管理

Copyright (c) 2026 by Senthie email: seemoon2077@gmail.com, All Rights Reserved.
"""

from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore',
        env_prefix='',  # No prefix for environment variables
    )

    # Application
    app_name: str = 'Low-Code Platform Backend'
    debug: bool = False
    host: str = '0.0.0.0'
    port: int = 8000
    api_v1_prefix: str = '/api/v1'

    # Security
    jwt_secret_key: str = Field(..., min_length=32)
    jwt_algorithm: str = 'HS256'
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    secret_key: Optional[str] = Field(
        default=None, min_length=32, description='Secret key for HMAC signing'
    )

    # Database - PostgreSQL
    database_url: str = Field(..., description='PostgreSQL connection URL')
    database_echo: bool = False
    database_pool_size: int = 5
    database_max_overflow: int = 10

    # MongoDB
    mongodb_url: str = Field(..., description='MongoDB connection URL')
    mongodb_database: str = 'lowcode_platform'

    # Redis
    redis_url: str = Field(..., description='Redis connection URL')
    redis_db: int = 0
    redis_max_connections: int = 10

    # Celery
    celery_broker_url: Optional[str] = None
    celery_result_backend: Optional[str] = None

    # Sentry
    sentry_dsn: Optional[str] = None
    sentry_environment: str = 'development'
    sentry_traces_sample_rate: float = 0.1

    # Logging
    log_level: str = 'INFO'
    log_format: str = 'json'

    # File Upload
    max_upload_size: int = 100 * 1024 * 1024  # 100MB
    gridfs_threshold: int = 16 * 1024 * 1024  # 16MB

    # CORS
    cors_origins: list[str] = ['http://localhost:3000']
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ['*']
    cors_allow_headers: list[str] = ['*']

    # SMTP邮件配置
    smtp_server: str = 'smtp.exmail.qq.com'  # 企业微信邮箱
    smtp_port: int = 465  # SSL端口
    smtp_username: str = ''
    smtp_password: str = ''
    from_email: str = 'noreply@yourcompany.com'
    frontend_url: str = 'https://yourapp.com'

    @field_validator('celery_broker_url', mode='before')
    @classmethod
    def set_celery_broker(cls, v: Optional[str], info) -> str:
        """Set Celery broker URL from Redis URL if not provided."""
        if v is None:
            redis_url = info.data.get('redis_url')
            if redis_url:
                return redis_url
        return v or ''

    @field_validator('celery_result_backend', mode='before')
    @classmethod
    def set_celery_backend(cls, v: Optional[str], info) -> str:
        """Set Celery result backend from Redis URL if not provided."""
        if v is None:
            redis_url = info.data.get('redis_url')
            if redis_url:
                return redis_url
        return v or ''

    @field_validator('secret_key', mode='before')
    @classmethod
    def set_secret_key(cls, v: Optional[str], info) -> str:
        """Set secret key from JWT secret if not provided."""
        if v is None:
            jwt_secret = info.data.get('jwt_secret_key')
            if jwt_secret:
                return jwt_secret
        return v or 'default-secret-key-for-development-only-change-in-production'


# Global settings instance
settings = Settings()  # type: ignore

if __name__ == '__main__':
    print(settings.mongodb_url)
    print(
        settings.jwt_secret_key
    )  # Output: redis://localhost:6379/0, default-secret-key-for-development-only-change-in-production
