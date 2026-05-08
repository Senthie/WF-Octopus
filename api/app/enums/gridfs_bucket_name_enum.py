"""
Author: '浪川' '1214391613@qq.com'
Date: 2026-05-08 14:31:19
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-05-08 14:49:44
FilePath: /api/app/enums/gridfs_bucket_name_enum.py
Description: GridFS 桶名称枚举及扩展名映射工具
Copyright (c) 2026 by '浪川' email: '1214391613@qq.com', All Rights Reserved.
"""

from enum import Enum
from typing import Dict, Final

# 模块级常量：扩展名（全大写）到桶名称字符串的映射（仅在模块加载时构建一次）
_EXTENSION_TO_BUCKET_VALUE: Final[Dict[str, str]] = {
    # 图片扩展名
    'BMP': 'image',
    'JPG': 'image',
    'JPEG': 'image',
    'PNG': 'image',
    'GIF': 'image',
    'TIFF': 'image',
    'PSD': 'image',
    'AI': 'image',
    'EPS': 'image',
    'SVG': 'image',
    'WEBP': 'image',
    'HEIC': 'image',
    # PDF
    'PDF': 'pdf',
    # 压缩文件扩展名
    'RAR': 'compressed_file',
    'ZIP': 'compressed_file',
    '7Z': 'compressed_file',
    'CAB': 'compressed_file',
    'ARJ': 'compressed_file',
    'LZH': 'compressed_file',
    'TAR': 'compressed_file',
    'GZ': 'compressed_file',
    'ACE': 'compressed_file',
    'UUE': 'compressed_file',
    'BZ2': 'compressed_file',
    'JAR': 'compressed_file',
    'ISO': 'compressed_file',
    'MPQ': 'compressed_file',
}


class GridfsBucketNameEnum(str, Enum):
    """GridFS 存储桶名称枚举（继承 str 以便直接作为字符串使用）"""

    IMAGE = 'image'
    PDF = 'pdf'
    COMPRESSED_FILE = 'compressed_file'
    UNKNOWN = 'unknown'

    @classmethod
    def get_bucket_by_extension(cls, file_extension: str) -> 'GridfsBucketNameEnum':
        """
        根据文件扩展名获取对应的 GridFS 桶枚举成员。

        Args:
            file_extension: 文件扩展名（可带前导点，如 '.jpg' 或 'jpg'）

        Returns:
            对应的枚举成员，若扩展名未知则返回 UNKNOWN
        """
        normalized = file_extension.lstrip('.').upper()
        value = _EXTENSION_TO_BUCKET_VALUE.get(normalized, 'unknown')
        return cls(value)  # 根据字符串值获取枚举成员


if __name__ == '__main__':
    # 调用方式（无需创建枚举实例）
    bucket = GridfsBucketNameEnum.get_bucket_by_extension('.jpg')
    print(bucket)  # <GridfsBucketNameEnum.IMAGE: 'image'>
    print(bucket.value)  # 'image'

    bucket = GridfsBucketNameEnum.get_bucket_by_extension('unknown')
    print(bucket)  # <GridfsBucketNameEnum.UNKNOWN: 'unknown'>
