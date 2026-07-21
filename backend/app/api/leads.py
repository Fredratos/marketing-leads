"""线索管理 API 路由"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, or_
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.models.database import Lead, Post, Comment, LeadFollowUp, User
from app.auth import get_current_user

router = APIRouter(prefix="/api/leads", tags=["线索管理"])


@router.get("")
async def list_leads(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    lead_type: Optional[str] = None,
    platform: Optional[str] = None,
    keyword: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    query = db.query(Lead).join(Post)

    if status:
        query = query.filter(Lead.status == status)
    if lead_type:
        query = query.filter(Lead.lead_type == lead_type)
    if platform:
        query = query.filter(Post.platform == platform)
    if keyword:
        like_kw = f"%{keyword}%"
        query = query.filter(
            or_(Post.title.ilike(like_kw), Post.content.ilike(like_kw), Post.author.ilike(like_kw))
        )
    if start_date:
        query = query.filter(Lead.created_at >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(Lead.created_at <= datetime.fromisoformat(end_date))

    total = query.count()
    leads = (
        query.order_by(desc(Lead.created_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    items = []
    for lead in leads:
        post = db.query(Post).filter(Post.id == lead.post_id).first()
        items.append({
            "id": lead.id,
            "post_id": lead.post_id,
            "title": post.title if post else "",
            "content": post.content[:200] if post else "",
            "author": post.author if post else "",
            "platform": post.platform if post else "",
            "permalink": post.permalink if post else "",
            "lead_type": lead.lead_type,
            "confidence": lead.confidence,
            "status": lead.status,
            "priority": lead.priority,
            "likes": post.likes if post else 0,
            "comments_count": post.comments_count if post else 0,
            "reason": lead.reason,
            "created_at": lead.created_at.isoformat() if lead.created_at else None,
            "updated_at": lead.updated_at.isoformat() if lead.updated_at else None,
        })

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items,
    }


@router.get("/{lead_id}")
async def get_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="线索不存在")

    post = db.query(Post).filter(Post.id == lead.post_id).first()
    comments = db.query(Comment).filter(Comment.post_id == lead.post_id).order_by(Comment.published_at.desc()).limit(50).all()
    follow_ups = db.query(LeadFollowUp).filter(LeadFollowUp.lead_id == lead_id).order_by(LeadFollowUp.created_at.desc()).all()

    return {
        "id": lead.id,
        "post_id": lead.post_id,
        "lead_type": lead.lead_type,
        "confidence": lead.confidence,
        "reason": lead.reason,
        "status": lead.status,
        "priority": lead.priority,
        "created_at": lead.created_at.isoformat() if lead.created_at else None,
        "updated_at": lead.updated_at.isoformat() if lead.updated_at else None,
        "post": {
            "id": post.id if post else None,
            "platform": post.platform if post else "",
            "platform_post_id": post.platform_post_id if post else "",
            "title": post.title if post else "",
            "content": post.content if post else "",
            "author": post.author if post else "",
            "author_avatar": post.author_avatar if post else "",
            "published_at": post.published_at.isoformat() if post and post.published_at else None,
            "likes": post.likes if post else 0,
            "collects": post.collects if post else 0,
            "comments_count": post.comments_count if post else 0,
            "images": post.images if post else [],
            "permalink": post.permalink if post else "",
        } if post else None,
        "comments": [
            {
                "id": c.id,
                "author": c.author,
                "content": c.content,
                "likes": c.likes,
                "published_at": c.published_at.isoformat() if c.published_at else None,
            } for c in comments
        ],
        "follow_ups": [
            {
                "id": f.id,
                "user_id": f.user_id,
                "content": f.content,
                "created_at": f.created_at.isoformat() if f.created_at else None,
            } for f in follow_ups
        ],
    }


@router.put("/{lead_id}/status")
async def update_lead_status(
    lead_id: int,
    body: dict,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="线索不存在")

    status = body.get("status")
    valid_statuses = ["新线索", "已查看", "已联系", "已转化", "无效"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"无效状态，可选值：{valid_statuses}")

    lead.status = status
    lead.updated_at = datetime.now()
    db.commit()

    return {"message": "状态已更新", "status": status}


@router.post("/{lead_id}/follow-ups")
async def add_follow_up(
    lead_idad_id: int,
    body: dict,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="线索不存在")

    content = body.get("content", "").strip()
    if not content:
        raise HTTPException(status_code=400, detail="跟进内容不能为空")

    follow_up = LeadFollowUp(
        lead_id=lead_id,
        user_id=user_id,
        content=content,
    )
    db.add(follow_up)
    db.commit()
    db.refresh(follow_up)

    return {
        "id": follow_up.id,
        "content": follow_up.content,
        "created_at": follow_up.created_at.isoformat(),
    }
