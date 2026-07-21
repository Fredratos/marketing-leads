"""Pydantic schemas"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


# User schemas
class UserCreate(BaseModel):
    email: str
    password: str
    nickname: Optional[str] = None


class UserOut(BaseModel):
    id: int
    email: str
    nickname: Optional[str]
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Keyword schemas
class KeywordGroupCreate(BaseModel):
    name: str
    keywords: list[str]
    exclude_keywords: list[str] = []
    platform: str = "xiaohongshu"
    crawl_interval: str = "daily"


class KeywordGroupOut(BaseModel):
    id: int
    name: str
    keywords: list[str]
    exclude_keywords: list[str]
    platform: str
    crawl_interval: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Lead schemas
class LeadOut(BaseModel):
    id: int
    post_id: int
    lead_type: Optional[str]
    confidence: float
    reason: Optional[str]
    status: str
    priority: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LeadDetailOut(LeadOut):
    title: Optional[str] = None
    content: Optional[str] = None
    author: Optional[str] = None
    platform: Optional[str] = None
    permalink: Optional[str] = None
    likes: int = 0
    comments_count: int = 0
    images: list = []


class LeadUpdateStatus(BaseModel):
    status: str


class FollowUpCreate(BaseModel):
    content: str


class FollowUpOut(BaseModel):
    id: int
    user_id: Optional[int]
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


# Pagination
class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    page_size: int
