"""SQLAlchemy 数据模型"""
from datetime import datetime, timedelta, timezone
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON, Index, Float
from app.core.database import Base

CN_TZ = timezone(timedelta(hours=8), name="Asia/Shanghai")

def now_cn():
    return datetime.now(CN_TZ)


class DataSource(Base):
    """数据集"""
    __tablename__ = "data_sources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False)
    slug = Column(String(128), unique=True, nullable=False, index=True)
    description = Column(Text, default="")

    # 汇总统计
    file_count = Column(Integer, default=0)
    total_size = Column(Integer, default=0)
    tags = Column(JSON, default=list)
    likes = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), default=now_cn)
    updated_at = Column(DateTime(timezone=True), default=now_cn, onupdate=now_cn)

    __table_args__ = (
        Index("ix_ds_name", "name"),
        Index("ix_ds_active", "is_active"),
    )


class DatasetFile(Base):
    """数据集内的单个文件"""
    __tablename__ = "dataset_files"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, nullable=False, index=True)
    file_name = Column(String(512), nullable=False)
    file_format = Column(String(16), default="")
    file_type = Column(String(16), default="")       # tabular / raw
    file_size = Column(Integer, default=0)
    file_content = Column(Text, default="")            # raw 类型存原文

    # tabular 元信息
    schema_definition = Column(JSON, default=dict)
    record_count = Column(Integer, default=0)
    columns = Column(JSON, default=list)

    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=now_cn)

    __table_args__ = (
        Index("ix_file_source", "source_id"),
    )


class DataRecord(Base):
    """数据记录 — 仅 tabular 文件使用"""
    __tablename__ = "data_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_id = Column(Integer, nullable=False, index=True)
    source_id = Column(Integer, nullable=False, index=True)
    data = Column(JSON, nullable=False)
    row_index = Column(Integer, default=0)
    version = Column(Integer, default=1)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=now_cn)
    updated_at = Column(DateTime(timezone=True), default=now_cn, onupdate=now_cn)

    __table_args__ = (
        Index("ix_record_file_deleted", "file_id", "is_deleted"),
    )


class ActivityLog(Base):
    """操作日志"""
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    action = Column(String(64), nullable=False)
    target_type = Column(String(64))
    target_id = Column(Integer)
    source_id = Column(Integer, nullable=True, index=True)
    detail = Column(Text, default="")
    status = Column(String(16), default="success")  # success / failed
    created_at = Column(DateTime(timezone=True), default=now_cn)

    __table_args__ = (
        Index("ix_log_action", "action"),
        Index("ix_log_status", "status"),
        Index("ix_log_time", "created_at"),
    )


class User(Base):
    """用户与角色"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    full_name = Column(String(128), default="")
    email = Column(String(256), default="")
    password_hash = Column(String(256), nullable=False)
    role = Column(String(16), default="user")  # admin / user
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=now_cn)

    __table_args__ = (
        Index("ix_user_role", "role"),
        Index("ix_user_active", "is_active"),
    )
