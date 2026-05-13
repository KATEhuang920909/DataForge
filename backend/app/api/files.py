"""文件上传/下载/预览/删除 — 路由前缀 /files 避免和 /sources/{id} 冲突"""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
from app.core.auth import get_optional_current_user, get_current_user, require_admin
from app.core.database import get_db
from app.schemas import DatasetFileOut, APIResponse
from app.services import get_files, get_file_by_id, upload_file, export_file, get_file_preview, delete_file, _log, get_source_by_id

router = APIRouter(prefix="/files", tags=["files"])

def _f(f): return DatasetFileOut.model_validate(f).model_dump()


@router.get("/list/{source_id}", response_model=APIResponse)
async def list_files(source_id: int, db: Session = Depends(get_db), current_user=Depends(get_optional_current_user)):
    files = get_files(db, source_id)
    return APIResponse(data={"items": [_f(f) for f in files], "total": len(files)})


@router.post("/upload/{source_id}", response_model=APIResponse)
async def upload(source_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), current_user=Depends(require_admin)):
    if not get_source_by_id(db, source_id):
        _log(db, "upload_file", "dataset_file", None, f"Failed: 数据集不存在", source_id=source_id, status="failed")
        db.commit()
        raise HTTPException(404, "数据集不存在")
    content = await file.read()
    if not content:
        _log(db, "upload_file", "dataset_file", None, f"Failed: {file.filename} 文件为空", source_id=source_id, status="failed")
        db.commit()
        raise HTTPException(400, "文件为空")
    if len(content) > 200*1024*1024:
        _log(db, "upload_file", "dataset_file", None, f"Failed: {file.filename} 文件大小超过200MB", source_id=source_id, status="failed")
        db.commit()
        raise HTTPException(400, "文件大小不能超过 200MB")
    try:
        f = upload_file(db, source_id, content, file.filename)
    except ValueError as e:
        _log(db, "upload_file", "dataset_file", None, f"Failed: {file.filename} - {str(e)}", source_id=source_id, status="failed")
        db.commit()
        raise HTTPException(400, str(e))
    except Exception as e:
        _log(db, "upload_file", "dataset_file", None, f"Failed: {file.filename} - 解析失败: {str(e)}", source_id=source_id, status="failed")
        db.commit()
        raise HTTPException(500, f"解析失败: {str(e)}")
    return APIResponse(message=f"已上传 {file.filename}", data=_f(f))


@router.get("/{file_id}", response_model=APIResponse)
async def get_file_info(file_id: int, db: Session = Depends(get_db), current_user=Depends(get_optional_current_user)):
    f = get_file_by_id(db, file_id)
    if not f: raise HTTPException(404, "文件不存在")
    return APIResponse(data=_f(f))


@router.get("/{file_id}/preview", response_model=APIResponse)
async def preview(file_id: int, db: Session = Depends(get_db), current_user=Depends(get_optional_current_user)):
    try: data = get_file_preview(db, file_id)
    except ValueError as e: raise HTTPException(404, str(e))
    return APIResponse(data=data)


@router.get("/{file_id}/download")
async def download(file_id: int, db: Session = Depends(get_db), current_user=Depends(get_optional_current_user)):
    f = get_file_by_id(db, file_id)
    if not f: raise HTTPException(404, "文件不存在")

    # 修复1：调用export_file获取处理后的文件名、内容、mime和编码后的文件名
    try:
        filename, content, mime, encoded_filename = export_file(db, file_id)
    except ValueError as e:
        raise HTTPException(404, str(e))

    # 修复2：按RFC 5987标准设置Content-Disposition，兼容中文文件名
    headers = {
        "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}",
        "Cache-Control": "no-cache"
    }

    # 记录下载日志
    _log(db, "download_file", "dataset_file", file_id, f"Downloaded: {filename}", source_id=f.source_id)
    db.commit()

    # 返回流式响应（修复响应头编码问题）
    return StreamingResponse(
        iter([content]),
        media_type=mime,
        headers=headers
    )


@router.delete("/{file_id}", response_model=APIResponse)
async def remove_file(file_id: int, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    try:
        if not delete_file(db, file_id):
            raise HTTPException(404, "文件不存在")
    except Exception as e:
        if isinstance(e, HTTPException): raise
        raise HTTPException(500, str(e))
    return APIResponse(message="文件已删除")