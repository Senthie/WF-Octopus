"""
Author: '浪川' '1214391613@qq.com'
Date: 2026-04-07 15:35:36
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-04-07 15:35:58
FilePath: /api/app/apis/v1/pdf.py
Description: get pdf files api point

Copyright (c) 2026 by '浪川' email: '1214391613@qq.com', All Rights Reserved.
"""

import shutil
from pathlib import Path
from typing import List
from uuid import uuid4

import fitz
from fastapi import APIRouter, File, UploadFile
from PIL import Image

from app.core.response import ResponseModel, response_base
from app.enums.response_code_enum import CustomResponseCodeEnum

router = APIRouter(prefix="/pdf", tags=["pdf v1"])


def sanitize_name(name: str) -> str:
    """将字符串中的空格和 U+00A0 替换为下划线"""
    # 替换普通空格和 U+00A0 (不换行空格)
    return name.replace(" ", "_").replace("\u00a0", "_")


def convert_pdf_to_images(pdf_path: Path, output_folder: Path, resolution=300):
    # 打开 PDF 文件
    pdf_document = fitz.open(pdf_path)
    # 遍历 PDF 中的每一页
    for page_number in range(len(pdf_document)):
        page = pdf_document[page_number]
        # 获取页面的原始大小（以点为单位）
        zoom_x = resolution / page.rect.width
        zoom_y = resolution / page.rect.height
        # 使用最小的缩放比例以确保整个页面都适应目标分辨率
        zoom = min(1, 1)
        # 创建一个矩阵来应用缩放和抗锯齿
        mat = fitz.Matrix(zoom, zoom)
        # 将 PDF 页面转换为图片
        pix = page.get_pixmap(matrix=mat)
        # 使用 PIL 的 Image 对象打开图片
        image = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        # 保存图片
        image_filename = f"{output_folder}/{pdf_path.stem}_{page_number + 1}.png"
        image.save(image_filename)

    # 关闭 PDF 文件
    pdf_document.close()


@router.post("/pdf2png", summary="pdf to png")
async def pdf2png(file: UploadFile = File(...)) -> ResponseModel:
    """
    接收一个pdf，将其转换为png图片并返回图片的路径
    """

    try:
        # prepare paths
        uploads_dir = Path("app/tmp/uploads")
        extract_base = Path("app/tmp/pdf2png")

        uploads_dir.mkdir(parents=True, exist_ok=True)
        extract_base.mkdir(parents=True, exist_ok=True)

        # 清洗上传的文件名
        orig_filename = file.filename or f"upload_{uuid4().hex}"
        clean_filename = sanitize_name(orig_filename)
        # 如果清洗后为空或产生冲突，加 uuid
        if not clean_filename:
            clean_filename = f"upload_{uuid4().hex}"

        saved_path = uploads_dir / clean_filename
        with saved_path.open("wb") as out_f:
            shutil.copyfileobj(file.file, out_f)

        # create unique extraction target（目录名也清洗）
        base_dir_name = sanitize_name(saved_path.stem) + "_" + uuid4().hex
        target_dir = extract_base / base_dir_name
        target_dir.mkdir(parents=True, exist_ok=True)

        convert_pdf_to_images(saved_path, target_dir)

        # sanitize_path(target_dir)

        # 收集清洗后的文件路径（相对 app/tmp 的路径）
        files: List[str] = [
            p.relative_to(Path("app/tmp")).as_posix()
            for p in target_dir.rglob("*")
            if p.is_file()
        ]

        return response_base.success(
            data={"extracted_dir": str(target_dir.resolve()), "files": files}
        )

    except Exception as e:
        return response_base.fail(
            res=CustomResponseCodeEnum.INTERNAL_SERVER_ERROR,
            data=f"Failed to extract archive: {str(e)}",
        )
