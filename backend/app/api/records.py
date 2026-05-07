"""数据记录 CRUD 接口"""
import math
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.auth import get_optional_current_user, require_admin
from app.core.database import get_db
from app.schemas import DataRecordCreate, DataRecordUpdate, DataRecordOut, APIResponse
from app.services import (
    create_record, get_records, get_record_by_id, update_record, soft_delete_record
)

router = APIRouter(prefix="/records", tags=["data-records"])


def _r(r) -> dict:
    return DataRecordOut.model_validate(r).model_dump()


@router.get("/", response_model=APIResponse)
async def list_records(
    source_id: int = Query(...),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_optional_current_user),
):
    items, total = get_records(db, source_id, page, size, keyword)
    return APIResponse(data={
        "items": [_r(r) for r in items],
        "total": total, "page": page, "page_size": size,
        "pages": math.ceil(total / size) if size else 0,
    })


@router.post("/", response_model=APIResponse, status_code=201)
async def create(body: DataRecordCreate, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    record = create_record(db, body)
    return APIResponse(message="记录创建成功", data=_r(record))


@router.get("/{record_id}", response_model=APIResponse)
async def get_record(record_id: int, db: Session = Depends(get_db), current_user=Depends(get_optional_current_user)):
    record = get_record_by_id(db, record_id)
    if not record:
        raise HTTPException(404, "记录不存在")
    return APIResponse(data=_r(record))


@router.patch("/{record_id}", response_model=APIResponse)
async def patch_record(record_id: int, body: DataRecordUpdate, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    record = update_record(db, record_id, body)
    if not record:
        raise HTTPException(404, "记录不存在")
    return APIResponse(message="更新成功", data=_r(record))


@router.delete("/{record_id}", response_model=APIResponse)
async def remove_record(record_id: int, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    if not soft_delete_record(db, record_id):
        raise HTTPException(404, "记录不存在")
    return APIResponse(message="删除成功")
