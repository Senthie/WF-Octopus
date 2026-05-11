import asyncio
import traceback

import httpx

from app.core.celery import celery_app
from app.core.pg_database import AsyncSessionLocal
from app.models.celery import CeleryTaskStatus
from app.utils.celery_db_help import CeleryDbHelp
from app.utils.timezone_help import tz_helper


@celery_app.task(name='ollama_generate', bind=True)
def ollama_generate(self, prompt: str, model: str = 'llama2', task_record_id: str = ''):
    """
    同步 Celery 任务，内部使用 asyncio.run 调用异步 Ollama 客户端。

    :param self: 任务实例（bind=True 时提供）
    :param prompt: 用户提示
    :param model: 模型名称
    :param task_record_id: 可选，数据库记录 ID（用于更新状态）
    """
    task_id = self.request.id  # Celery 任务 ID

    async def _run():
        # 可选：更新数据库状态为 started
        if task_record_id:
            async with AsyncSessionLocal() as session:
                server = CeleryDbHelp(session)
                await server.update_task_status(
                    task_id,
                    CeleryTaskStatus.STARTED,
                    started_at=tz_helper.get_current_time('Asia/Shanghai'),
                )
        try:
            payload = {
                'model': 'qwen3:8b',
                'prompt': prompt,
                'stream': False,
                'images': [],  # 注意是列表
            }
            # 调用 Ollama
            resp = httpx.post(
                'http://14.12.0.172:11434/api/generate',  # 使用默认端口 11434
                json=payload,
                timeout=30.0,
            )
            resp.raise_for_status()
            result = resp.json()

            # 更新数据库为成功
            if task_record_id:
                async with AsyncSessionLocal() as session:
                    server = CeleryDbHelp(session)
                    await server.update_task_status(
                        task_id,
                        CeleryTaskStatus.SUCCESS,
                        result={'answer': result},
                        ended_at=tz_helper.get_current_time('Asia/Shanghai'),
                    )
            return result.get('response', 'No response field')

        except Exception as e:
            error_msg = traceback.format_exc()
            if task_record_id:
                async with AsyncSessionLocal() as session:
                    server = CeleryDbHelp(session)
                    await server.update_task_status(
                        task_id,
                        CeleryTaskStatus.FAILURE,
                        error=error_msg,
                        ended_at=tz_helper.get_current_time('Asia/Shanghai'),
                    )
            # 可选：触发重试
            raise self.retry(exc=e, countdown=60, max_retries=3)

    return asyncio.run(_run())
