"""
Author: '浪川' '1214391613@qq.com'
Date: 2026-04-03 15:57:55
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-04-23 10:52:49
FilePath: /api/app/enums/response_code_enum.py
Description:自定义响应代码和信息

Copyright (c) 2026 by '浪川' email: '1214391613@qq.com', All Rights Reserved.
"""

from enum import Enum


class CustomCodeBase(Enum):
    """自定义状态码基类"""

    @property
    def code(self) -> int:
        """获取状态码"""
        return self.value[0]

    @property
    def msg(self) -> str:
        """获取状态码信息"""
        message = self.value[1]
        return message


class CustomResponseCodeEnum(CustomCodeBase):
    # 通用状态码
    SUCCESS = (200, '请求成功')
    BAD_REQUEST = (400, '请求参数错误')
    UNAUTHORIZED = (401, '身份验证未通过')
    FORBIDDEN = (403, '客户端没有访问内容的权限')
    NOT_FOUND = (404, '请求的资源不存在')
    INTERNAL_SERVER_ERROR = (500, '服务器内部错误')

    UNKNOWN_ERROR = (999, '未知错误')
    # Auth
    EMAIL_ALREADY_EXISTS = (1001, '邮箱已存在')
    PASSWORD_TOO_SHORT = (1002, '密码长度至少8位')
    PASSWORD_MISSING_UPPERCASE = (1003, '密码必须包含至少一个大写字母')
    PASSWORD_MISSING_LOWERCASE = (1004, '密码必须包含至少一个小写字母')
    PASSWORD_MISSING_DIGIT = (1005, '密码必须包含至少一个数字')

    # AI 巡检
    INSPECTION_RECORD_NOT_FOUND = (2001, '巡检记录未找到')

    # 巡检要求
    INSPECTION_REQUIREMENT_NOT_FOUND = (3001, '巡检要求未找到')
