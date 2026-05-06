"""业务服务层"""
import io
import json
from datetime import datetime
from typing import Optional
from pathlib import Path

import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func, String

from app.models import DataSource, DatasetFile, DataRecord, ActivityLog
from app.schemas import DataSourceCreate, DataSourceUpdate

TABULAR_FORMATS = {'csv', 'json', 'xlsx', 'xls', 'tsv'}


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
    # Delete all files + records
    file_ids = [f.id for f in db.query(DatasetFile).filter(DatasetFile.source_id == source_id).all()]
    if file_ids:
        db.query(DataRecord).filter(DataRecord.file_id.in_(file_ids)).delete()
    db.query(DatasetFile).filter(DatasetFile.source_id == source_id).delete()
    _log(db, "delete_source", "data_source", source_id, f"Deleted: {source.name}", source_id=source_id)
    db.delete(source); db.commit()
    return True


def _update_source_stats(db: Session, source_id: int):
    """重新计算数据集的文件数和总大小"""
    files = db.query(DatasetFile).filter(DatasetFile.source_id == source_id).all()
    source = get_source_by_id(db, source_id)
    if source:
        source.file_count = len(files)
        source.total_size = sum(f.file_size for f in files)
        source.updated_at = datetime.utcnow()
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
    db.query(DataRecord).filter(DataRecord.file_id == file_id).delete()
    _log(db, "delete_file", "dataset_file", file_id, f"Deleted: {f.file_name}", source_id=sid)
    db.delete(f)
    _update_source_stats(db, sid)
    db.commit()
    db.expire_all()
    return True


def upload_file(db: Session, source_id: int, content: bytes, filename: str) -> DatasetFile:
    """上传文件到数据集（追加，不替换）"""
    source = get_source_by_id(db, source_id)
    if not source: raise ValueError("数据集不存在")

    ext = Path(filename).suffix.lstrip('.').lower()
    file_size = len(content)

    # 获取当前最大 sort_order
    max_order = db.query(func.max(DatasetFile.sort_order)).filter(
        DatasetFile.source_id == source_id).scalar() or 0

    df = DatasetFile(
        source_id=source_id, file_name=filename, file_format=ext,
        sort_order=max_order + 1,
    )

    if ext in TABULAR_FORMATS:
        rows, columns, schema_def = _parse_tabular(content, ext)
    else:
        rows = []

    # Flush file to get ID before adding records
    db.add(df)
    db.flush()

    if ext in TABULAR_FORMATS:
        for idx, row_data in enumerate(rows):
            db.add(DataRecord(file_id=df.id, source_id=source_id, data=row_data, row_index=idx))
        db.flush()
        df.file_type = "tabular"
        df.record_count = len(rows)
        df.columns = columns
        df.schema_definition = schema_def
        detail = f"{filename} ({ext}, {len(rows)} rows × {len(columns)} cols)"
    else:
        try: text = content.decode('utf-8')
        except UnicodeDecodeError: text = content.decode('latin-1')
        df.file_type = "raw"
        df.file_content = text
        df.record_count = len(text.splitlines())
        df.columns = []
        df.schema_definition = {"content_type": "text", "lines": df.record_count}
        detail = f"{filename} ({ext}, {df.record_count} lines)"
    df.file_size = file_size
    _update_source_stats(db, source_id)
    _log(db, "upload_file", "dataset_file", df.id, detail, source_id=source_id)
    db.commit(); db.refresh(df)
    return df


def _parse_tabular(content: bytes, ext: str):
    if ext == 'tsv': df = pd.read_csv(io.BytesIO(content), sep='\t')
    elif ext == 'csv': df = pd.read_csv(io.BytesIO(content))
    elif ext == 'json':
        raw = json.loads(content)
        df = pd.DataFrame(raw if isinstance(raw, list) else raw)
    elif ext in ('xlsx', 'xls'): df = pd.read_excel(io.BytesIO(content), engine='openpyxl')
    else: df = pd.read_csv(io.BytesIO(content))
    df = df.where(pd.notnull(df), None)
    columns = list(df.columns)
    schema_def = {}
    for col in columns:
        dtype_str = str(df[col].dtype)
        sample = []
        for v in df[col].dropna().head(3).tolist():
            if hasattr(v, 'item'): v = v.item()
            sample.append(v)
        schema_def[col] = {"type": dtype_str, "nullable": bool(df[col].isna().any()), "sample": sample}
    rows = []
    for idx, row in df.iterrows():
        row_data = {}
        for col in columns:
            val = row[col]
            if hasattr(val, 'item'): val = val.item()
            if pd.isna(val): val = None
            row_data[col] = val
        rows.append(row_data)
    return rows, columns, schema_def


# ── File Download ──

def export_file(db: Session, file_id: int, fmt: str = "original"):
    f = get_file_by_id(db, file_id)
    if not f: raise ValueError("文件不存在")
    safe_name = Path(f.file_name).stem.replace(" ", "_")

    if f.file_type == "raw":
        text = f.file_content or ""
        if fmt in ("original", f.file_format, ""):
            ext = f.file_format or "txt"
            mime_map = {"md":"text/markdown","py":"text/x-python","js":"text/javascript","ts":"text/typescript","html":"text/html","css":"text/css","json":"application/json","txt":"text/plain","yaml":"text/yaml","yml":"text/yaml","toml":"text/plain","csv":"text/csv","log":"text/plain","xml":"text/xml","sh":"text/x-shellscript","sql":"text/plain"}
            mime = mime_map.get(ext, "text/plain")
            return f"{safe_name}.{ext}", text.encode('utf-8'), mime
        elif fmt == "json":
            data = {"content": text, "source_file": f.file_name, "format": f.file_format}
            return f"{safe_name}.json", json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8'), "application/json"
        else:
            return f"{safe_name}.{f.file_format}", text.encode('utf-8'), "text/plain"

    records = db.query(DataRecord).filter(
        DataRecord.file_id == file_id, DataRecord.is_deleted == False
    ).order_by(DataRecord.row_index).all()
    if not records: raise ValueError("数据集为空")
    data = [r.data for r in records]
    df = pd.DataFrame(data)
    if fmt == "csv":
        buf = io.StringIO(); df.to_csv(buf, index=False)
        return f"{safe_name}.csv", buf.getvalue().encode('utf-8-sig'), "text/csv"
    elif fmt == "json":
        return f"{safe_name}.json", json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8'), "application/json"
    elif fmt == "xlsx":
        buf = io.BytesIO(); df.to_excel(buf, index=False, engine='openpyxl')
        return f"{safe_name}.xlsx", buf.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    else:
        buf = io.StringIO(); df.to_csv(buf, index=False)
        return f"{safe_name}.csv", buf.getvalue().encode('utf-8-sig'), "text/csv"


# ── Preview ──

def get_file_preview(db: Session, file_id: int) -> dict:
    f = get_file_by_id(db, file_id)
    if not f: raise ValueError("文件不存在")

    if f.file_type == "raw":
        text = f.file_content or ""
        lines = text.splitlines()
        return {"type": "raw", "file_name": f.file_name, "format": f.file_format,
                "file_size": f.file_size, "total_lines": len(lines), "preview_lines": lines[:200]}
    else:
        records = db.query(DataRecord).filter(
            DataRecord.file_id == file_id, DataRecord.is_deleted == False
        ).order_by(DataRecord.row_index).limit(100).all()
        return {"type": "tabular", "file_name": f.file_name, "format": f.file_format,
                "columns": f.columns, "total_rows": f.record_count,
                "preview": [{"row_index": r.row_index, "data": r.data} for r in records]}


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
    log = ActivityLog(action=action, target_type=target_type, target_id=target_id, source_id=source_id, detail=detail, status=status)
    db.add(log)
    db.flush()
