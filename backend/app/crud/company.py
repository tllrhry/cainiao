"""
公司信息 CRUD 操作
KV 结构：按 key 读写公司信息（名称、简介、联系方式等）
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.company import CompanyInfo


def get_all(db: Session) -> List[CompanyInfo]:
    """获取所有公司信息配置（按 key 排序）"""
    return db.query(CompanyInfo).order_by(CompanyInfo.key.asc()).all()


def get_by_key(db: Session, key: str) -> Optional[CompanyInfo]:
    """按 key 获取单条配置"""
    return db.query(CompanyInfo).filter(CompanyInfo.key == key).first()


def upsert(db: Session, key: str, value: str, type: str = "text") -> CompanyInfo:
    """创建或更新一条配置"""
    record = db.query(CompanyInfo).filter(CompanyInfo.key == key).first()
    if record:
        record.value = value
        record.type = type
    else:
        record = CompanyInfo(key=key, value=value, type=type)
        db.add(record)
    db.commit()
    db.refresh(record)
    return record
