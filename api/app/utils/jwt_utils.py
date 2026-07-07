"""
Author: kk123047 3254834740@qq.com
Date: 2025-12-09 18:00:00
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-04-28 14:13:01
FilePath: /api/app/utils/token.py
Description: 令牌工具

Copyright (c) 2026 by Senthie email: seemoon2077@gmail.com, All Rights Reserved.
"""

"""JWT token generation and verification utilities."""
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from uuid import UUID

import jwt

from app.core.config import settings


class TokenType:
    """Token type constants."""

    ACCESS = 'access'
    REFRESH = 'refresh'


def generate_access_token(user_id: UUID, additional_claims: Optional[Dict[str, Any]] = None) -> str:
    """
    Generate JWT access token.

    Args:
        user_id: User UUID
        additional_claims: Additional claims to include in token

    Returns:
        Encoded JWT access token
    """
    payload = {
        'user_id': str(user_id),
        'type': TokenType.ACCESS,
        'exp': datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes),
        'iat': datetime.now(timezone.utc),
    }

    if additional_claims:
        payload.update(additional_claims)

    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return token


def generate_refresh_token(user_id: UUID) -> str:
    """
    Generate JWT refresh token.

    Args:
        user_id: User UUID

    Returns:
        Encoded JWT refresh token
    """
    payload = {
        'user_id': str(user_id),
        'type': TokenType.REFRESH,
        'exp': datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days),
        'iat': datetime.now(timezone.utc),
    }

    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return token


def verify_token(token: str, token_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Verify JWT token and return payload.

    Args:
        token: JWT token to verify
        token_type: Expected token type (access or refresh)

    Returns:
        Token payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])

        # Verify token type if specified
        if token_type and payload.get('type') != token_type:
            return None

        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode JWT token without verification (for debugging).

    Args:
        token: JWT token to decode

    Returns:
        Token payload if decodable, None otherwise
    """
    try:
        payload = jwt.decode(token, options={'verify_signature': False})
        return payload
    except jwt.InvalidTokenError:
        return None
