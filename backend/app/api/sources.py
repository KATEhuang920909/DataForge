"""数据集 CRUD"""
import math
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas import DataSourceCreate, DataSourceUpdate, DataSourceOut, APIResponse
from app.services import create_source, get_sources, get_source_by_id, update_source, delete_source, like_source, _log

router = APIRouter(prefix="/sources", tags=["data-sources"])

def _s(s): return DataSourceOut.model_validate(s).model_dump()

@router.get("/", response_model=APIResponse)
async def list_sources(page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=100),
                      active_only: bool = False, tag: Optional[str] = None,
                      keyword: Optional[str] = None, db: Session = Depends(get_db)):
    items, total = get_sources(db, page, size, active_only, tag, keyword)
    return APIResponse(data={"items": [_s(s) for s in items], "total": total,
                             "page": page, "page_size": size, "pages": math.ceil(total/size) if size else 0})

@router.post("/", response_model=APIResponse, status_code=201)
async def create(body: DataSourceCreate, db: Session = Depends(get_db)):
    try: 
        source = create_source(db, body)
    except Exception as e:
        error_msg = str(e)
        if "UNIQUE constraint" in error_msg: 
            _log(db, "create_source", "data_source", None, f"Failed: Slug '{body.slug}' already exists", status="failed")
            db.commit()
            raise HTTPException(400, f"Slug '{body.slug}' already exists")
        _log(db, "create_source", "data_source", None, f"Failed: {error_msg}", status="failed")
        db.commit()
        raise
    return APIResponse(message="数据集创建成功", data=_s(source))

@router.get("/{source_id}", response_model=APIResponse)
async def get_source(source_id: int, db: Session = Depends(get_db)):
    source = get_source_by_id(db, source_id)
    if not source: raise HTTPException(404, "数据集不存在")
    return APIResponse(data=_s(source))

@router.patch("/{source_id}", response_model=APIResponse)
async def patch(source_id: int, body: DataSourceUpdate, db: Session = Depends(get_db)):
    try:
        source = update_source(db, source_id, body)
        if not source: raise HTTPException(404, "数据集不存在")
    except Exception as e:
        _log(db, "update_source", "data_source", source_id, f"Failed: {str(e)}", source_id=source_id, status="failed")
        db.commit()
        if isinstance(e, HTTPException): raise
        raise HTTPException(500, str(e))
    return APIResponse(message="更新成功", data=_s(source))

@router.post("/{source_id}/like", response_model=APIResponse)
async def like(source_id: int, db: Session = Depends(get_db)):
    source = like_source(db, source_id)
    if not source: 
        _log(db, "like_source", "data_source", source_id, "Failed: 数据集不存在", source_id=source_id, status="failed")
        db.commit()
        raise HTTPException(404, "数据集不存在")
    _log(db, "like_source", "data_source", source_id, f"Liked: {source.name}", source_id=source_id)
    db.commit()
    return APIResponse(data={"likes": source.likes})

@router.delete("/{source_id}", response_model=APIResponse)
async def remove(source_id: int, db: Session = Depends(get_db)):
    try:
        if not delete_source(db, source_id): 
            _log(db, "delete_source", "data_source", source_id, "Failed: 数据集不存在", source_id=source_id, status="failed")
            db.commit()
            raise HTTPException(404, "数据集不存在")
    except Exception as e:
        if isinstance(e, HTTPException): raise
        _log(db, "delete_source", "data_source", source_id, f"Failed: {str(e)}", source_id=source_id, status="failed")
        db.commit()
        raise HTTPException(500, str(e))
    return APIResponse(message="删除成功")
