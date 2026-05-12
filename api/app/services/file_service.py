import base64
from typing import AsyncGenerator, Optional
from uuid import UUID

from fastapi import UploadFile
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.exceptions import FileException
from app.core.logging import get_logger
from app.core.storage.gridfs import GridFSBackend
from app.enums import CustomResponseCodeEnum
from app.enums.gridfs_bucket_name_enum import GridfsBucketNameEnum
from app.models.auth.user import UserModel
from app.models.file.reference import FileReferenceModel
from app.schemas import FileReferenceOut
from app.schemas.page_schema import PageReq, PageRes

logger = get_logger(__name__)


class FileService:
    """文件服务

    协调 PostgreSQL 元数据和 MongoDB GridFS 存储。
    """

    def __init__(self, session: AsyncSession):
        """初始化文件服务

        Args:
            session: 数据库会话
        """
        self.session = session

    async def upload_file(
        self,
        file: UploadFile,
        user: UserModel,
    ) -> FileReferenceModel:
        """上传文件

        流程：
        1. 上传文件到 GridFS
        2. 在 PostgreSQL 创建元数据记录
        3. 如果失败，回滚 GridFS 文件

        Args:
            file: 上传的文件对象
            workspace_id: 工作空间 ID
            uploaded_by: 上传者用户 ID

        Returns:
            FileReference: 文件引用记录

        Raises:
            FileUploadError: 上传失败
        """
        mongo_id = None
        user_id = user.id
        bucket_name_type = GridfsBucketNameEnum.get_bucket_by_extension(
            file.content_type.split('/')[1]
        )
        storage = GridFSBackend(bucket_name_type)
        try:
            # 先获取文件类型，决定将文件扔到什么桶

            # 1. 上传到 GridFS
            metadata = {
                'uploaded_by': str(user_id),
            }

            mongo_id = await storage.upload(file, metadata=metadata)

            # 2. 确定存储类型（根据文件大小）
            file_size = file.size or 0

            # 3. 创建 PostgreSQL 元数据记录
            file_reference = FileReferenceModel(
                gridfs_id=mongo_id,
                filename=file.filename or 'unknown',
                content_type=file.content_type or 'application/octet-stream',
                size_bytes=file_size,
                bucket_name_type=bucket_name_type,
                created_by=user_id,  # pyright: ignore[reportCallIssue]
                updated_by=user_id,  # pyright: ignore[reportCallIssue]
            )

            self.session.add(file_reference)
            await self.session.commit()
            await self.session.refresh(file_reference)

            return file_reference

        except Exception as e:
            # 回滚：删除已上传的 GridFS 文件
            if mongo_id:
                try:
                    await storage.delete(mongo_id)
                    logger.info('Rolled back GridFS file', mongo_id=mongo_id)
                except Exception as rollback_error:
                    logger.error(
                        'Failed to rollback GridFS file',
                        mongo_id=mongo_id,
                        error=str(rollback_error),
                    )

            await self.session.rollback()

            logger.error(
                'Failed to upload file',
                filename=file.filename,
                error=str(e),
            )
            raise

    async def download_file(
        self, file_id: UUID
    ) -> tuple[FileReferenceModel, AsyncGenerator[bytes, None]]:
        """下载文件

        Args:
            file_id: 文件 ID

        Returns:
            tuple: (文件元数据, 文件内容流)

        Raises:
            FileNotFoundError: 文件不存在
        """
        # 1. 查询 PostgreSQL 元数据
        statement = select(FileReferenceModel).where(FileReferenceModel.id == file_id)
        result = await self.session.execute(statement)
        file_reference: FileReferenceModel = result.scalar_one_or_none()  # type: ignore

        if not file_reference:
            logger.warning('File not found in database', file_id=str(file_id))
            raise FileException(CustomResponseCodeEnum.FILE_NOT_FIND, f'{file_id} NOT Finad')
        storage = GridFSBackend(file_reference.bucket_name_type)
        # 2. 从 GridFS 下载文件流
        file_stream = storage.download(file_reference.gridfs_id)

        logger.info(
            'File download started',
            file_id=str(file_id),
            filename=file_reference.filename,
        )

        return file_reference, file_stream

    async def delete_by_id(self, file_id: UUID, user: UserModel) -> bool:
        """删除文件

        流程：
        1. 删除 PostgreSQL 元数据
        2. 删除 GridFS 文件
        3. 如果 GridFS 删除失败，记录日志但不回滚

        Args:
            file_id: 文件 ID

        Returns:
            bool: 删除成功返回 True
        """
        # 1. 查询文件元数据
        statement = select(FileReferenceModel).where(FileReferenceModel.id == file_id)
        result = await self.session.execute(statement)
        file_reference: FileReferenceModel = result.scalar_one_or_none()  # type: ignore

        if not file_reference:
            logger.warning('File not found for deletion', file_id=str(file_id))
            return False

        gridfs_id = file_reference.gridfs_id

        storage = GridFSBackend(file_reference.bucket_name_type)
        try:
            # 2. 删除 PostgreSQL 记录
            file_reference.soft_delete()
            file_reference.updated_by = user.id
            await self.session.commit()

            # 3. 删除 GridFS 文件（最佳努力，失败不回滚）
            try:
                await storage.delete(gridfs_id)
                logger.info(
                    'File deleted successfully',
                    file_id=str(file_id),
                    gridfs_id=gridfs_id,
                )
            except Exception as storage_error:
                logger.error(
                    'Failed to delete GridFS file (metadata already deleted)',
                    file_id=str(file_id),
                    gridfs_id=gridfs_id,
                    error=str(storage_error),
                )

            return True

        except Exception as e:
            await self.session.rollback()
            logger.error(
                'Failed to delete file',
                file_id=str(file_id),
                error=str(e),
            )
            raise

    async def get_file_metadata(self, file_id: UUID) -> Optional[FileReferenceModel]:
        """获取文件元数据

        Args:
            file_id: 文件 ID

        Returns:
            FileReference: 文件引用记录，不存在返回 None
        """
        statement = select(FileReferenceModel).where(FileReferenceModel.id == file_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def list_files(self, page_req: PageReq) -> PageRes[FileReferenceOut]:
        """列出工作空间的文件

        Args:
            workspace_id: 工作空间 ID
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            list[FileReference]: 文件列表
        """
        offset = (page_req.current - 1) * page_req.size
        statement = (
            select(FileReferenceModel)
            .order_by(FileReferenceModel.created_at.desc())
            .limit(page_req.maxLimit)
            .offset(offset)
        )

        result = await self.session.execute(statement)
        datas = result.scalars().all()
        items = [FileReferenceOut.model_validate(f) for f in datas]

        count_statement = (
            select(FileReferenceModel).where(FileReferenceModel.is_deleted != True)  # noqa: E712
        )
        count_result = await self.session.execute(count_statement)

        total = len(count_result.scalars().all())
        page_res = PageRes.model_validate(page_req.model_dump())
        page_res.records = items
        page_res.total = total

        return page_res

    async def get_image_base64_from_storage(self, file_id: UUID) -> str:
        """从存储中下载图片并返回 base64 字符串"""
        # 假设你已经有了 service 实例和 session
        file_reference, file_stream = await self.download_file(file_id)

        # 读取异步生成器中的所有字节
        try:
            chunks = []
            async for chunk in file_stream:
                chunks.append(chunk)
            full_bytes = b''.join(chunks)
        except Exception as e:
            logger.error(f'Error downloading file: {e}')
            raise

        # 转换为 base64
        base64_str = base64.b64encode(full_bytes).decode('utf-8')
        return base64_str
