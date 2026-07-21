"""统计分析 API"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.database import get_db
from app.models.database import Lead, Post
from app.auth import get_current_user

router = APIRouter(prefix="/api/stats", tags=["统计分析"])


@router.get("/dashboard")
async def dashboard(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    total_leads = db.query(Lead).count()
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_new = db.query(Lead).filter(Lead.created_at >= today).count()

    status_counts = {}
    for status in ["新线索", "已查看", "已联系", "已转化", "无效"]:
        status_counts[status] = db.query(Lead).filter(Lead.status == status).count()

    type_counts = {}
    for lead_type in ["找资源", "咨询求助", "经验分享", "资源展示"]:
        type_counts[lead_type] = db.query(Lead).filter(Lead.lead_type == lead_type).count()

    # Daily trend for last 7 days
    trend = []
    for i in range(6, -1, -1):
        day_start = today - timedelta(days=i)
        day_end = day_start + timedelta(days=1)
        count = db.query(Lead).filter(
            Lead.created_at >= day_start,
            Lead.created_at < day_end
        ).count()
        trend.append({"date": day_start.strftime("%m-%d"), "count": count})

    # Top keywords (from post titles)
    platform_counts = {}
    platforms = db.query(Post.platform).distinct().all()
    for (p,) in platforms:
        if p:
            platform_counts[p] = db.query(Post).filter(Post.platform == p).count()

    return {
        "total_leads": total_leads,
        "today_new": today_new,
        "status_counts": status_counts,
        "type_counts": type_counts,
        "daily_trend": trend,
        "platform_counts": platform_counts,
    }
