"""业务服务层"""
import base64
import hashlib
import hmac
import io
import json
import os
import re
from datetime import datetime
from typing import Optional
from pathlib import Path

import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func, String
from datetime import datetime, timedelta, timezone

from app.core.security import pwd_context
from app.models import DataSource, DatasetFile, DataRecord, ActivityLog, User
from app.schemas import DataSourceCreate, DataSourceUpdate, UserCreate, UserUpdate

# 配置项
TABULAR_FORMATS = {'csv', 'json', 'xlsx', 'xls', 'tsv'}
LOCAL_FILE_STORAGE = Path("./data/local_files").resolve()  # 转为绝对路径，避免相对路径错误
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB 最大文件限制，避免内存溢出
SAFE_FILENAME_REGEX = re.compile(r'[^\w\u4e00-\u9fa5\-\.]')  # 过滤非法文件名

# 初始化存储目录
LOCAL_FILE_STORAGE.mkdir(parents=True, exist_ok=True)


# ── DataSource CRUD ──

def create_source(db: Session, data: DataSourceCreate) -> DataSource:
    source = DataSource(**data.model_dump())
    db.add(source)
    db.flush()
    _log(db, "create_source", "data_source", source.id, f"Created: {source.name}", source_id=source.id)
    db.commit()
    db.refresh(source)
    return source


def get_sources(db: Session, page=1, size=20, active_only=False, tag=None, keyword=None):
    query = db.query(DataSource)
    if active_only: query = query.filter(DataSource.is_active == True)
    if tag: query = query.filter(DataSource.tags.contains([tag]))
    if keyword: query = query.filter(DataSource.name.ilike(f"%{keyword}%"))
    total = query.count()
    items = query.order_by(DataSource.updated_at.desc()).offset((page-1)*size).limit(size).all()

    if items:
        source_ids = [source.id for source in items]
        stats = db.query(
            DatasetFile.source_id,
            func.count(DatasetFile.id),
            func.coalesce(func.sum(DatasetFile.file_size), 0)
        ).filter(DatasetFile.source_id.in_(source_ids)).group_by(DatasetFile.source_id).all()
        stats_map = {sid: (count, total_size) for sid, count, total_size in stats}

        for source in items:
            count, total_size = stats_map.get(source.id, (0, 0))
            source.file_count = count
            source.total_size = total_size
        db.flush()

    return items, total


def get_source_by_id(db: Session, source_id: int) -> Optional[DataSource]:
    return db.query(DataSource).filter(DataSource.id == source_id).first()


def update_source(db: Session, source_id: int, data: DataSourceUpdate) -> Optional[DataSource]:
    source = get_source_by_id(db, source_id)
    if not source: return None
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(source, k, v)
    _log(db, "update_source", "data_source", source.id, f"Updated: {source.name}", source_id=source.id)
    db.commit(); db.refresh(source)
    return source


def like_source(db: Session, source_id: int) -> Optional[DataSource]:
    source = get_source_by_id(db, source_id)
    if not source: return None
    source.likes += 1; db.commit(); db.refresh(source)
    return source


def delete_source(db: Session, source_id: int) -> bool:
    source = get_source_by_id(db, source_id)
    if not source: return False
    file_ids = [f.id for f in db.query(DatasetFile).filter(DatasetFile.source_id == source_id).all()]
    if file_ids:
        # 统一删除本地文件
        for f in db.query(DatasetFile).filter(DatasetFile.source_id == source_id).all():
            if f.local_file_path and Path(f.local_file_path).exists():
                try:
                    os.remove(f.local_file_path)
                except Exception as e:
                    print(f"删除本地文件失败: {e}")
        db.query(DataRecord).filter(DataRecord.file_id.in_(file_ids)).delete()
    db.query(DatasetFile).filter(DatasetFile.source_id == source_id).delete()
    _log(db, "delete_source", "data_source", source_id, f"Deleted: {source.name}", source_id=source_id)
    db.delete(source); db.commit()
    return True


def _update_source_stats(db: Session, source_id: int):
    files = db.query(DatasetFile).filter(DatasetFile.source_id == source_id).all()
    source = get_source_by_id(db, source_id)
    if source:
        source.file_count = len(files)
        source.total_size = sum(f.file_size for f in files)
        source.updated_at = datetime.now(timezone(timedelta(hours=8)))
        db.flush()


# ── DatasetFile CRUD ──

def get_files(db: Session, source_id: int):
    return db.query(DatasetFile).filter(
        DatasetFile.source_id == source_id
    ).order_by(DatasetFile.sort_order, DatasetFile.created_at).all()


def get_file_by_id(db: Session, file_id: int) -> Optional[DatasetFile]:
    return db.query(DatasetFile).filter(DatasetFile.id == file_id).first()


def delete_file(db: Session, file_id: int) -> bool:
    f = get_file_by_id(db, file_id)
    if not f: return False
    sid = f.source_id
    # 统一删除本地文件
    if f.local_file_path and Path(f.local_file_path).exists():
        try:
            os.remove(f.local_file_path)
        except Exception as e:
            print(f"删除本地文件失败: {e}")
    db.query(DataRecord).filter(DataRecord.file_id == file_id).delete()
    _log(db, "delete_file", "dataset_file", file_id, f"Deleted: {f.file_name}", source_id=sid)
    db.delete(f)
    _update_source_stats(db, sid)
    db.commit()
    db.expire_all()
    return True


def _save_file_to_local(content: bytes, source_id: int, file_id: int, filename: str) -> str:
    """
    统一保存文件到本地（结构化/非结构化共用）
    修复：过滤非法文件名、绝对路径、异常捕获
    路径规则：./data/local_files/{source_id}/{file_id}_{安全文件名}.后缀
    """
    # 1. 校验参数
    if not file_id:
        raise ValueError("file_id 不能为空，必须先flush数据库获取自增ID")
    if len(content) > MAX_FILE_SIZE:
        raise ValueError(f"文件大小超过限制，最大支持{MAX_FILE_SIZE/1024/1024}MB")

    # 2. 安全处理文件名
    file_path = Path(filename)
    file_ext = file_path.suffix.lower()
    safe_stem = SAFE_FILENAME_REGEX.sub('_', file_path.stem.strip())[:100]  # 限制文件名长度
    unique_filename = f"{file_id}_{safe_stem}{file_ext}"

    # 3. 生成安全路径
    source_dir = LOCAL_FILE_STORAGE / str(source_id)
    source_dir.mkdir(parents=True, exist_ok=True)
    full_file_path = source_dir / unique_filename

    # 4. 写入文件（带异常捕获）
    try:
        with open(full_file_path, 'wb') as out:
            out.write(content)
    except Exception as e:
        raise RuntimeError(f"写入本地文件失败: {str(e)}") from e

    return str(full_file_path)


def upload_file(db: Session, source_id: int, content: bytes, filename: str) -> DatasetFile:
    """
    修复核心执行顺序：先flush获取file_id，再写入本地
    增加结构化文件解析容错、异常捕获
    """
    # 1. 基础校验
    source = get_source_by_id(db, source_id)
    if not source:
        raise ValueError("数据集不存在")
    if not content:
        raise ValueError("文件内容不能为空")

    ext = Path(filename).suffix.lstrip('.').lower()
    file_size = len(content)

    # 2. 获取排序序号
    max_order = db.query(func.max(DatasetFile.sort_order)).filter(
        DatasetFile.source_id == source_id).scalar() or 0

    # 3. 创建文件记录（先不存local_file_path）
    df = DatasetFile(
        source_id=source_id,
        file_name=filename,
        file_format=ext,
        sort_order=max_order + 1,
        file_size=file_size
    )

    # 🔥 核心修复：先flush到数据库，拿到自增的df.id
    db.add(df)
    db.flush()

    # 4. 现在有了正确的file_id，再写入本地文件
    try:
        local_file_path = _save_file_to_local(content, source_id, df.id, filename)
        df.local_file_path = local_file_path
        db.flush()  # 更新local_file_path到数据库
    except Exception as e:
        # 写入本地失败，回滚数据库记录
        db.rollback()
        raise RuntimeError(f"文件上传失败: {str(e)}") from e

    # 5. 处理结构化文件（解析、入库）
    if ext in TABULAR_FORMATS:
        try:
            rows, columns, schema_def = _parse_tabular(content, ext)
            # 批量插入记录，提升性能
            if rows:
                db.bulk_insert_mappings(
                    DataRecord,
                    [
                        {
                            "file_id": df.id,
                            "source_id": source_id,
                            "data": row_data,
                            "row_index": idx
                        }
                        for idx, row_data in enumerate(rows)
                    ]
                )
                db.flush()

            df.file_type = "tabular"
            df.record_count = len(rows)
            df.columns = columns
            df.schema_definition = schema_def
            detail = f"{filename} ({ext}, {len(rows)}行 × {len(columns)}列) | 已存本地"
        except Exception as e:
            # 解析失败，回滚所有操作
            db.rollback()
            # 同时删除已经写入的本地文件
            if Path(local_file_path).exists():
                os.remove(local_file_path)
            raise RuntimeError(f"结构化文件解析失败: {str(e)}") from e
    else:
        # 6. 处理非结构化文件（仅前100行入库）
        try:
            # 兼容编码
            try:
                text = content.decode('utf-8')
            except UnicodeDecodeError:
                text = content.decode('latin-1')

            all_lines = text.splitlines()
            total_lines = len(all_lines)
            preview_text = '\n'.join(all_lines[:100])

            df.file_type = "raw"
            df.file_content = preview_text
            df.record_count = total_lines
            df.columns = []
            df.schema_definition = {
                "content_type": "text",
                "total_lines": total_lines,
                "preview_lines": 100,
                "local_file_path": local_file_path
            }
            detail = f"{filename} ({ext}, {total_lines}行 | 前100行预览 | 已存本地)"
        except Exception as e:
            db.rollback()
            if Path(local_file_path).exists():
                os.remove(local_file_path)
            raise RuntimeError(f"非结构化文件处理失败: {str(e)}") from e

    # 7. 最终提交
    _update_source_stats(db, source_id)
    _log(db, "upload_file", "dataset_file", df.id, detail, source_id=source_id)
    db.commit()
    db.refresh(df)
    return df


def _parse_tabular(content: bytes, ext: str):
    """
    修复：xlsx指定openpyxl引擎、csv中文编码兼容、空文件容错
    """
    # 空文件处理
    if len(content) == 0:
        return [], [], {}

    # 1. 读取文件
    if ext == 'tsv':
        df = pd.read_csv(io.BytesIO(content), sep='\t')
    elif ext == 'csv':
        # 兼容中文编码
        try:
            df = pd.read_csv(io.BytesIO(content), encoding='utf-8-sig')
        except:
            try:
                df = pd.read_csv(io.BytesIO(content), encoding='gbk')
            except:
                df = pd.read_csv(io.BytesIO(content), encoding='gb2312')
    elif ext == 'json':
        raw = json.loads(content)
        df = pd.DataFrame(raw if isinstance(raw, list) else raw)
    elif ext in ('xlsx', 'xls'):
        # 修复：xlsx指定openpyxl引擎，避免环境缺失报错
        df = pd.read_excel(io.BytesIO(content), engine='openpyxl' if ext == 'xlsx' else None)
    else:
        df = pd.read_csv(io.BytesIO(content))

    # 2. 空值处理
    df = df.where(pd.notnull(df), None)
    columns = list(df.columns)
    schema_def = {}

    # 3. 生成字段schema
    for col in columns:
        dtype_str = str(df[col].dtype)
        sample = []
        for v in df[col].dropna().head(3).tolist():
            if hasattr(v, 'item'):
                v = v.item()
            sample.append(v)
        schema_def[col] = {
            "type": dtype_str,
            "nullable": bool(df[col].isna().any()),
            "sample": sample
        }

    # 4. 生成行数据
    rows = []
    for idx, row in df.iterrows():
        row_data = {}
        for col in columns:
            val = row[col]
            if hasattr(val, 'item'):
                val = val.item()
            if pd.isna(val):
                val = None
            row_data[col] = val
        rows.append(row_data)

    return rows, columns, schema_def


# ── File Download ──

def export_file(db: Session, file_id: int, fmt: str = "original"):
    """
    修复：xlsx导出引擎、csv中文编码、本地文件读取容错
    新增：中文文件名响应头编码，解决latin-1编码报错
    """
    f = get_file_by_id(db, file_id)
    if not f:
        raise ValueError("文件不存在")
    safe_name = SAFE_FILENAME_REGEX.sub('_', Path(f.file_name).stem.strip())[:100]

    # 1. 优先从本地读取原文件
    if f.local_file_path and Path(f.local_file_path).exists():
        try:
            with open(f.local_file_path, 'rb') as infile:
                original_content = infile.read()
        except Exception as e:
            raise RuntimeError(f"读取本地文件失败: {str(e)}") from e

        # 原格式导出
        if fmt == "original":
            ext = f.file_format or "txt"
            mime_map = {
                "md": "text/markdown",
                "py": "text/x-python",
                "js": "text/javascript",
                "ts": "text/typescript",
                "html": "text/html",
                "css": "text/css",
                "json": "application/json",
                "txt": "text/plain",
                "yaml": "text/yaml",
                "yml": "text/yaml",
                "toml": "text/plain",
                "csv": "text/csv",
                "log": "text/plain",
                "xml": "text/xml",
                "sh": "text/x-shellscript",
                "sql": "text/plain",
                "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "xls": "application/vnd.ms-excel"
            }
            mime = mime_map.get(ext, "application/octet-stream")
            filename = f"{safe_name}.{ext}"

        # JSON格式导出
        elif fmt == "json":
            if f.file_type == "raw":
                try:
                    text = original_content.decode('utf-8')
                except UnicodeDecodeError:
                    text = original_content.decode('latin-1')
                data = {
                    "source_file": f.file_name,
                    "format": f.file_format,
                    "content": text
                }
                filename = f"{safe_name}.json"
                original_content = json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8')
                mime = "application/json"
            else:
                records = db.query(DataRecord).filter(
                    DataRecord.file_id == file_id, DataRecord.is_deleted == False
                ).order_by(DataRecord.row_index).all()
                data = [r.data for r in records]
                filename = f"{safe_name}.json"
                original_content = json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8')
                mime = "application/json"

        # CSV格式导出（仅结构化）
        elif fmt == "csv" and f.file_type == "tabular":
            records = db.query(DataRecord).filter(
                DataRecord.file_id == file_id, DataRecord.is_deleted == False
            ).order_by(DataRecord.row_index).all()
            data = [r.data for r in records]
            df = pd.DataFrame(data)
            buf = io.StringIO()
            df.to_csv(buf, index=False, encoding='utf-8-sig')
            original_content = buf.getvalue().encode('utf-8')
            filename = f"{safe_name}.csv"
            mime = "text/csv"

        # XLSX格式导出（仅结构化）
        elif fmt == "xlsx" and f.file_type == "tabular":
            records = db.query(DataRecord).filter(
                DataRecord.file_id == file_id, DataRecord.is_deleted == False
            ).order_by(DataRecord.row_index).all()
            data = [r.data for r in records]
            df = pd.DataFrame(data)
            buf = io.BytesIO()
            df.to_excel(buf, index=False)
            original_content = buf.getvalue()
            filename = f"{safe_name}.xlsx"
            mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        # 其他格式兜底
        else:
            filename = f"{safe_name}.{f.file_format}"
            mime = "application/octet-stream"

        # 核心修复：对中文文件名进行URL编码，兼容HTTP响应头
        from urllib.parse import quote
        # 生成RFC 5987标准的文件名响应头
        encoded_filename = quote(filename, encoding='utf-8')
        return filename, original_content, mime, encoded_filename
    else:
        raise ValueError("本地文件不存在，无法导出，请重新上传文件")


# ── Preview ──

def get_file_preview(db: Session, file_id: int) -> dict:
    f = get_file_by_id(db, file_id)
    if not f: raise ValueError("文件不存在")

    if f.file_type == "raw":
        text = f.file_content or ""
        lines = text.splitlines()
        return {
            "type": "raw",
            "file_name": f.file_name,
            "format": f.file_format,
            "file_size": f.file_size,
            "total_lines": f.record_count,
            "preview_lines": lines,
            "note": "预览仅前100行，完整文件已存本地"
        }
    else:
        records = db.query(DataRecord).filter(
            DataRecord.file_id == file_id, DataRecord.is_deleted == False
        ).order_by(DataRecord.row_index).limit(100).all()
        return {
            "type": "tabular",
            "file_name": f.file_name,
            "format": f.file_format,
            "columns": f.columns,
            "total_rows": f.record_count,
            "preview": [{"row_index": r.row_index, "data": r.data} for r in records],
            "note": "完整源文件已存本地"
        }


# ── DataRecord ──

def get_records(db: Session, source_id: int, page=1, size=20, keyword=None):
    query = db.query(DataRecord).filter(DataRecord.source_id == source_id, DataRecord.is_deleted == False)
    if keyword: query = query.filter(DataRecord.data.cast(String).ilike(f"%{keyword}%"))
    total = query.count()
    items = query.order_by(DataRecord.row_index).offset((page-1)*size).limit(size).all()
    return items, total


# ── ActivityLog ──

def get_logs(db: Session, page=1, size=20, source_id=None):
    query = db.query(ActivityLog)
    if source_id:
        query = query.filter(ActivityLog.source_id == source_id)
    total = query.count()
    items = query.order_by(ActivityLog.created_at.desc()).offset((page-1)*size).limit(size).all()
    return items, total


def _log(db, action, target_type, target_id, detail, source_id=None, status="success"):
    log = ActivityLog(
        action=action,
        target_type=target_type,
        target_id=target_id,
        source_id=source_id,
        detail=detail,
        status=status
    )
    db.add(log)
    db.flush()


# ── User 管理 ──

def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_user(db: Session, user_in: UserCreate) -> User:
    hashed_password = pwd_context.hash(user_in.password)
    db_user = User(
        username=user_in.username,
        password_hash=hashed_password,
        email=user_in.email,
        full_name=user_in.full_name,
        role='user'
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def list_users(db: Session, page=1, size=50):
    query = db.query(User).order_by(User.created_at.desc())
    total = query.count()
    items = query.offset((page-1)*size).limit(size).all()
    return items, total


def update_user(db: Session, user_id: int, data: UserUpdate) -> Optional[User]:
    user = get_user_by_id(db, user_id)
    if not user: return None
    payload = data.model_dump(exclude_unset=True)
    if 'password' in payload and payload['password'] is not None:
        user.password_hash = pwd_context.hash(payload.pop('password'))
    if 'role' in payload and payload['role'] not in ('admin', 'user'):
        payload['role'] = 'user'
    for key, value in payload.items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int) -> bool:
    user = get_user_by_id(db, user_id)
    if not user: return False
    db.delete(user)
    db.commit()
    return True