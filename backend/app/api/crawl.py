"""采集管理 API"""
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.database import KeywordGroup, CrawlLog
from app.auth import get_current_user
from app.services.crawler import crawl_posts_by_keywords

router = APIRouter(prefix="/api/crawl", tags=["采集管理"])


@router.post("/{keyword_group_id}")
async def trigger_crawl(
    keyword_group_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    group = db.query(KeywordGroup).filter(KeywordGroup.id == keyword_group_id).first()
    if not group:
        return {"error": "关键词组不存在"}

    if not group.is_active:
        return {"error": "关键词组已停用"}

    # Trigger crawl in background
    background_tasks.add_task(
        crawl_posts_by_keywords,
        db, keyword_group_id, group.keywords, group.exclude_keywords
    )

    return {"message": "采集任务已触发", "keyword_group": group.name}


@router.get("/logs")
async def crawl_logs(
    limit: int = 20,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    logs = db.query(CrawlLog).order_by(CrawlLog.started_at.desc()).limit(limit).all()
    return [
        {
            "id": log.id,
            "keyword_group_id": log.keyword_group_id,
            "status": log.status,
            "total_found": log.total_found,
            "new_leads": log.new_leads,
            "error_message": log.error_message,
            "started_at": log.started_at.isoformat() if log.started_at else None,
            "finished_at": log.finished_at.isoformat() if log.finished_at else None,
        } for log in logs
    ]
