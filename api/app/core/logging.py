"""
Author: '浪川' '1214391613@qq.com'
Date: 2026-04-21 11:11:46
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-04-21 12:09:57
FilePath: /api/app/core/logging.py
Description:structlog 日志配置（集成 Rich 美化）

Copyright (c) 2026 by '浪川' email: '1214391613@qq.com', All Rights Reserved.
"""

import logging
import sys
from typing import Any

from rich.console import Console
from rich.text import Text
from rich.traceback import install
import structlog
from structlog.types import EventDict

from app.core.config import settings

# 安装 Rich 的 traceback 处理器，美化异常输出
install()

# 创建一个全局 Rich Console 实例
console = Console()


def add_app_context(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """添加应用上下文到日志事件中"""
    event_dict['app'] = settings.app_name
    event_dict['environment'] = settings.sentry_environment
    return event_dict


def rich_console_renderer(logger: Any, method_name: str, event_dict: EventDict) -> str:
    """
    自定义的 Rich 渲染器，将结构化日志事件以美观的格式输出到终端。
    该处理器会直接使用 Rich Console 打印日志，并返回空字符串，
    避免后续处理器（如 JSONRenderer）再次输出。
    """
    # 提取常用字段
    level = event_dict.get('level', 'info')
    event = event_dict.get('event', '')
    timestamp = event_dict.get('timestamp', '')
    logger_name = event_dict.get('logger', '')
    # 额外字段（排除已使用的标准字段）
    extra = {
        k: v
        for k, v in event_dict.items()
        if k not in ('level', 'event', 'timestamp', 'logger', 'app', 'environment')
    }

    # 根据日志级别设定颜色
    level_colors = {
        'debug': 'cyan',
        'info': 'green',
        'warning': 'yellow',
        'error': 'red',
        'critical': 'red bold',
    }
    level_color = level_colors.get(level, 'white')

    # 构建 Rich Text 对象
    text = Text()
    text.append(f'[{timestamp}] ', style='dim')
    text.append(f'[{logger_name}] ', style='blue')
    text.append(f'[{level.upper()}] ', style=level_color)
    text.append(event, style='default')
    if extra:
        text.append(f' {extra}', style='magenta')

    # 直接打印到 Rich Console
    console.print(text)
    # 返回空字符串，防止 structlog 再调用后续 processor（如 JSONRenderer）
    return ''


def configure_logging() -> None:
    """配置结构化日志（开发环境使用 Rich 美化，生产环境使用 JSON）"""

    # 根据配置选择最终的渲染器
    if settings.log_format == 'json':
        # 生产环境：输出 JSON 格式，不经过 Rich 渲染
        processors: list[Any] = [
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt='iso'),
            add_app_context,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),  # 最终输出 JSON
        ]
    else:
        # 开发环境：使用 Rich 美化输出
        processors = [
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt='iso'),
            add_app_context,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            rich_console_renderer,  # 自定义 Rich 渲染器作为最终步骤
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # 配置标准库的 logging（structlog 最终会调用标准库日志）
    # 注意：由于我们在 Rich 渲染器中直接打印到终端，且返回了空字符串，
    # 标准库的 handler 将收到空消息。为避免产生空行，可以设置一个 NullHandler。
    # 但为了保持兼容性（例如某些模块直接使用 logging 记录日志），保留 basicConfig
    # 并设置一个简单格式，让这些日志也能输出。
    logging.basicConfig(
        format='%(message)s',
        stream=sys.stdout,
        level=getattr(logging, settings.log_level.upper()),
    )
    # 如果 structlog 的渲染器已经打印了日志，不希望标准库再输出空行，可以将 root logger 的级别设为 CRITICAL
    # 或者自定义 filter 过滤空消息。以下提供一个可选方案：
    if settings.log_format != 'json':
        # 为 root logger 添加一个过滤器，丢弃空消息
        class EmptyMessageFilter(logging.Filter):
            def filter(self, record):
                return bool(record.getMessage().strip())

        logging.getLogger().addFilter(EmptyMessageFilter())


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """获取结构化日志记录器"""
    return structlog.get_logger(name)
