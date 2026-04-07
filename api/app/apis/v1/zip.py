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


def sanitize_name(name: str) -> str:
    """将字符串中的空格和 U+00A0 替换为下划线"""
    # 替换普通空格和 U+00A0 (不换行空格)
    return name.replace(" ", "_").replace("\u00a0", "_")


def sanitize_path(path: Path) -> Path:
    """
    递归重命名路径下的所有文件和目录，将空格/U+00A0替换为下划线。
    返回重命名后的根路径（即传入的路径可能被重命名）。
    """
    if not path.exists():
        return path

    # 如果路径是文件夹
    # 先处理子内容（深度优先），再处理自身，避免父目录改名后子路径失效
    if path.is_dir():
        for child in sorted(path.iterdir(), key=lambda p: len(p.parts), reverse=True):
            sanitize_path(child)

    # 处理当前路径的名称
    new_name = sanitize_name(path.name)
    if new_name != path.name:
        new_path = path.parent / new_name
        # 如果目标已存在，添加唯一后缀（防止冲突）
        if new_path.exists():
            counter = 1
            while new_path.exists():
                stem = new_name
                # 分离扩展名
                if "." in new_name:
                    base, ext = new_name.rsplit(".", 1)
                    new_name = f"{base}_{counter}.{ext}"
                else:
                    new_name = f"{new_name}_{counter}"
                new_path = path.parent / new_name
                counter += 1
        path.rename(new_path)
        return new_path
    return path


@router.post("/unzip", summary="Upload and extract a zip/tar/gz archive")
async def unzip_file(file: UploadFile = File(...)) -> ResponseModel:
    """接收一个压缩包 (zip/tar/tar.gz/gz)，解压并返回文件地址列表。"""

    try:
        # prepare paths
        uploads_dir = Path("app/tmp/uploads")
        extract_base = Path("app/tmp/extracted")

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

        name_l = orig_filename.lower()  # 用于判断格式，用原始名称即可

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
            out_name = target_dir / sanitize_name(saved_path.stem)
            with gzip.open(saved_path, "rb") as gz_f, out_name.open("wb") as out_f:
                shutil.copyfileobj(gz_f, out_f)
        else:
            return response_base.fail(
                res=CustomResponseCodeEnum.BAD_REQUEST,
                data=f"Unsupported archive format: {orig_filename}",
            )

        # 解压完成后，对 target_dir 下所有文件和目录进行重命名（递归清洗）
        sanitize_path(target_dir)

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
