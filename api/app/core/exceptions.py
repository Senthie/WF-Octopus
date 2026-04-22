"""
Author: '浪川' '1214391613@qq.com'
Date: 2026-04-21 17:02:55
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-04-21 17:03:50
FilePath: /api/app/core/exceptions.py
Description:

Copyright (c) 2026 by '浪川' email: '1214391613@qq.com', All Rights Reserved.
"""

from app.enums import CustomResponseCodeEnum


class AiInspectionException(Exception):
    """Business logic exception with custom response code."""

    def __init__(self, response_code: CustomResponseCodeEnum, message: str | None = None):
        self.response_code = response_code
        self.message = message or response_code.msg
        super().__init__(self.message)
