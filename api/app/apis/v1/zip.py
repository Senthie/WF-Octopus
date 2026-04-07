"""
Author: '浪川' '1214391613@qq.com'
Date: 2026-04-03 12:15:27
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-04-03 15:16:11
FilePath: /api/app/apis/v1/zip.py
Description:压缩操作的主要api接口

Copyright (c) 2026 by '浪川' email: '1214391613@qq.com', All Rights Reserved.
"""

import gzip
import shutil
import tarfile
import zipfile
from pathlib import Path
from typing import List
from uuid import uuid4

from fastapi import APIRouter, File, UploadFile

from app.core.response import ResponseModel, response_base
from app.enums.response_code_enum import CustomResponseCodeEnum

router = APIRouter(prefix="/zip", tags=["zip v1"])


@router.post("/unzip", summary="Upload and extract a zip/tar/gz archive")
async def unzip_file(file: UploadFile = File(...)) -> ResponseModel:
    """接收一个压缩包 (zip/tar/tar.gz/gz)，解压并返回文件地址列表。"""

    try:
        # prepare paths
        uploads_dir = Path("app/tmp/uploads")
        extract_base = Path("app/tmp/extracted")

        uploads_dir.mkdir(parents=True, exist_ok=True)
        extract_base.mkdir(parents=True, exist_ok=True)

        # save uploaded file
        orig_filename = file.filename or f"upload_{uuid4().hex}"
        saved_path = uploads_dir / orig_filename
        with saved_path.open("wb") as out_f:
            shutil.copyfileobj(file.file, out_f)

        # create unique extraction target
        target_dir = extract_base / (saved_path.stem + "_" + uuid4().hex)
        target_dir.mkdir(parents=True, exist_ok=True)

        name_l = orig_filename.lower()

        # extract based on format
        if name_l.endswith(".zip"):
            with zipfile.ZipFile(saved_path, "r") as zf:
                zf.extractall(target_dir)
        elif name_l.endswith((".tar", ".tar.gz", ".tgz")) or tarfile.is_tarfile(
            saved_path
        ):
            with tarfile.open(saved_path, "r:*") as tf:
                tf.extractall(target_dir)
        elif name_l.endswith(".gz") and not name_l.endswith(".tar.gz"):
            # single-file gzip
            out_name = target_dir / Path(saved_path.stem)
            with gzip.open(saved_path, "rb") as gz_f, out_name.open("wb") as out_f:
                shutil.copyfileobj(gz_f, out_f)
        else:
            # unsupported format
            return response_base.fail(
                res=CustomResponseCodeEnum.BAD_REQUEST,
                data=f"Unsupported archive format: {orig_filename}",
            )

        # collect extracted file paths
        files: List[str] = [
            str(p.resolve()) for p in target_dir.rglob("*") if p.is_file()
        ]

        return response_base.success(
            data={"extracted_dir": str(target_dir.resolve()), "files": files}
        )

    except Exception as e:
        return response_base.fail(
            res=CustomResponseCodeEnum.INTERNAL_SERVER_ERROR,
            data=f"Failed to extract archive: {str(e)}",
        )
