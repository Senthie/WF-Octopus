"""
Author: '浪川' '1214391613@qq.com'
Date: 2026-04-28 15:56:27
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-04-28 16:04:03
FilePath: /api/app/middlewares/auth.py
Description:

Copyright (c) 2026 by '浪川' email: '1214391613@qq.com', All Rights Reserved.
"""

from typing import Callable

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.pg_database import get_session
from app.core.redis import get_redis
from app.models import UserModel
from app.services.auth_service import AuthService

http_bearer = HTTPBearer()


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware for authentication."""

    async def dispatch(self, request: Request, call_next: Callable):
        """
        Process request and verify authentication.

        Args:
            request: FastAPI request
            call_next: Next middleware/handler

        Returns:
            Response from next handler
        """
        # Skip authentication for public endpoints
        public_paths = [
            '/docs',
            '/redoc',
            '/openapi.json',
            '/health',
            '/',
            '/api/v1/auth/register',
            '/api/v1/auth/login',
            '/api/v1/auth/refresh',
            '/api/v1/auth/reset-password',
            '/api/v1/auth/confirm-reset-password',
        ]

        if request.url.path in public_paths:
            return await call_next(request)

        # Get authorization header
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            # Allow request to proceed - individual endpoints can enforce auth
            return await call_next(request)

        # Extract token
        token = auth_header.replace('Bearer ', '')

        # Verify token and attach user to request state
        try:
            # Get database session using async generator
            session_gen = get_session()
            db = await anext(session_gen)

            try:
                redis = await get_redis()
                auth_service = AuthService(db, redis)
                user = await auth_service.verify_access_token(token)

                if user:
                    request.state.user = user
                    request.state.token = token
            finally:
                # Close the session properly
                await session_gen.aclose()
        except (ValueError, RuntimeError, ConnectionError):
            # If verification fails, continue without user
            pass

        response = await call_next(request)
        return response


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
) -> UserModel:
    """
    Dependency to get current authenticated user via OAuth2 Bearer token.

    Args:
        token: Bearer token extracted by oauth2_scheme

    Returns:
        Current user

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Not authenticated',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        session_gen = get_session()
        db = await anext(session_gen)
        try:
            redis = await get_redis()
            auth_service = AuthService(db, redis)
            user = await auth_service.verify_access_token(credentials.credentials)
            if not user:
                raise credentials_exception
            return user
        finally:
            await session_gen.aclose()
    except HTTPException:
        raise
    except Exception:
        raise credentials_exception
