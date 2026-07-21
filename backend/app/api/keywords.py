"""关键词管理 API 路由"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models.database import KeywordGroup
from app.auth import get_current_user

router = APIRouter(prefix="/api/keywords", tags=["关键词管理"])


@router.get("")
async def list_keywords(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    groups = db.query(KeywordGroup).order_by(KeywordGroup.created_at.desc()).all()
    return [
        {
            "id": g.id,
            "name": g.name,
            "keywords": g.keywords,
            "exclude_keywords": g.exclude_keywords,
            "platform": g.platform,
            "crawl_interval": g.crawl_interval,
            "is_active": g.is_active,
            "created_at": g.created_at.isoformat() if g.created_at else None,
        } for g in groups
    ]


@router.post("")
async def create_keyword(
    body: dict,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    name = body.get("name", "").strip()
    keywords = body.get("keywords", [])
    if not name or not keywords:
        raise HTTPException(status_code=400, detail="名称和关键词不能为空")

    group = KeywordGroup(
        name=name,
        keywords=keywords,
        exclude_keywords=body.get("exclude_keywords", []),
        platform=body.get("platform", "xiaohongshu"),
        crawl_interval=body.get("crawl_interval", "daily"),
    )
    db.add(group)
    db.commit()
    db.refresh(group)

    return {"id": group.id, "message": "关键词组创建成功"}


@router.put("/{group_id}")
async def update_keyword(
    group_id: int,
    body: dict,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    group = db.query(KeywordGroup).filter(KeywordGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="关键词组不存在")

    if "name" in body:
        group.name = body["name"]
    if "keywords" in body:
        group.keywords = body["keywords"]
    if "exclude_keywords" in body:
        group.exclude_keywords = body["exclude_keywords"]
    if "platform" in body:
        group.platform = body["platform"]
    if "crawl_interval" in body:
        group.crawl_interval = body["crawl_interval"]
    if "is_active" in body:
        group.is_active = body["is_active"]
    group.updated_at = datetime.now()

    db.commit()
    return {"message": "关键词组已更新"}


@router.delete("/{group_id}")
async def delete_keyword(
    group_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    group = db.query(KeywordGroup).filter(KeywordGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="关键词组不存在")

    db.delete(group)
    db.commit()
    return {"message": "关键词组已删除"}
