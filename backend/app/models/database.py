"""数据库模型"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    nickname = Column(String(100))
    role = Column(String(50), default="viewer")  # admin, editor, viewer
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class KeywordGroup(Base):
    """关键词组配置"""

    __tablename__ = "keyword_groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    keywords = Column(JSON, nullable=False)  # ["海外达人", "海外KOL"]
    exclude_keywords = Column(JSON, default=[])
    platform = Column(String(50), default="xiaohongshu")  # xiaohongshu, douyin, etc.
    crawl_interval = Column(String(20), default="daily")  # hourly, 6hourly, daily, weekly
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class Post(Base):
    """采集到的原始帖子"""

    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String(50), nullable=False)  # xiaohongshu, douyin
    platform_post_id = Column(String(100), nullable=False)  # 平台原始帖子ID
    title = Column(String(500))
    content = Column(Text)
    author = Column(String(200))
    author_id = Column(String(100))
    published_at = Column(DateTime)
    likes = Column(Integer, default=0)
    collects = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    images = Column(JSON, default=[])  # 图片URL列表
    permalink = Column(String(500))  # 原始链接
    raw_data = Column(JSON, default={})  # 原始JSON数据
    keyword_group_id = Column(Integer, ForeignKey("keyword_groups.id"))
    created_at = Column(DateTime, default=datetime.now)


class Comment(Base):
    """帖子评论"""

    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False Kick, index=True)
    author = Column(String(200))
    content = Column(Text)
    published_at = Column(DateTime)
    likes = Column(Integer, default=0)
    raw_data = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.now)

    post = relationship("Post")


class Lead(Base):
    """营销线索"""

    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), unique=True)
    lead_type = Column(String(50))  # 找资源, 咨询求助, 经验分享, 资源展示
    confidence = Column(Float, default=0.0)
    reason = Column(Text)  # AI判定理由
    status = Column(String(20), default="新线索")  # 新线索, 已查看, 已联系, 已转化, 无效
    priority = Column(Integer, default=0)  # 优先级 0-5
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    post = relationship("Post")


class LeadFollowUp(Base):
    """线索跟进记录"""

    __tablename__ = "lead_follow_ups"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    lead = relationship("Lead")


class OperationLog(Base):
    """操作日志"""

    __tablename__ = "operation_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(100))  # create, update, delete, export
    target_type = Column(String(50))  # lead, keyword, user
    target_id = Column(Integer)
    detail = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.now)
