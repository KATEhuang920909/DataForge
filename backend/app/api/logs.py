"""操作日志"""
import math
from typing import Optional
from datetime import timezone, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas import APIResponse, ActivityLogOut
from app.services import get_logs
from app.models import DataSource

CN_TZ = timezone(timedelta(hours=8), name="Asia/Shanghai")

def to_beijing(dt):
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(CN_TZ).isoformat()

router = APIRouter(prefix="/logs", tags=["logs"])

@router.get("/", response_model=APIResponse)
async def list_logs(page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=100),
                   source_id: Optional[int] = Query(None),
                   db: Session = Depends(get_db)):
    items, total = get_logs(db, page, size, source_id)
    
    # 补充source_name信息
    result_items = []
    for l in items:
        log_data = {
            "id": l.id,
            "action": l.action,
            "target_type": l.target_type,
            "target_id": l.target_id,
            "source_id": l.source_id,
            "detail": l.detail,
            "status": l.status,
            "created_at": to_beijing(l.created_at),
            "source_name": None
        }
        if l.source_id:
            source = db.query(DataSource).filter(DataSource.id == l.source_id).first()
            if source:
                log_data["source_name"] = source.name
        result_items.append(log_data)
    
    return APIResponse(data={
        "items": result_items,
        "total": total, "page": page, "page_size": size,
        "pages": math.ceil(total/size) if size else 0,
    })
