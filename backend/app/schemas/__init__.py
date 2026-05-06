"""Pydantic 数据模式"""
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field


class DataSourceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    slug: str = Field(..., min_length=1, max_length=128, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    description: str = Field(default="", max_length=2000)
    tags: list[str] = Field(default_factory=list)


class DataSourceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=128)
    description: Optional[str] = Field(None, max_length=2000)
    is_active: Optional[bool] = None
    tags: Optional[list[str]] = None


class DataSourceOut(BaseModel):
    id: int
    name: str
    slug: str
    description: str
    file_count: int
    total_size: int
    tags: list[str]
    likes: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class DatasetFileOut(BaseModel):
    id: int
    source_id: int
    file_name: str
    file_format: str
    file_type: str
    file_size: int
    schema_definition: dict[str, Any]
    record_count: int
    columns: list[str]
    sort_order: int
    created_at: datetime
    model_config = {"from_attributes": True}


class DataRecordCreate(BaseModel):
    source_id: int
    data: dict[str, Any]
    tags: list[str] = Field(default_factory=list)


class DataRecordUpdate(BaseModel):
    data: Optional[dict[str, Any]] = None
    tags: Optional[list[str]] = None


class DataRecordOut(BaseModel):
    id: int
    file_id: int
    source_id: int
    data: dict[str, Any]
    row_index: int
    version: int
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class ActivityLogOut(BaseModel):
    id: int
    action: str
    target_type: Optional[str]
    target_id: Optional[int]
    source_id: Optional[int] = None
    source_name: Optional[str] = None
    detail: str
    status: str = "success"  # success / failed
    created_at: datetime
    model_config = {"from_attributes": True}


class APIResponse(BaseModel):
    success: bool = True
    message: str = "ok"
    data: Any = None
