"""采集服务 - 搜索采集帖子 + LLM分类"""
import httpx
from loguru import logger
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from app.services.llm_service import classify_lead
from app.models.database import Post, Comment, Lead, CrawlLog


async def search_posts_from_web(query: str, platform: str = "xiaohongshu", max_results: int = 20) -> list:
    """通过网络搜索获取帖子列表"""
    try:
        search_url = f"https://www.google.com/search?q=site:xiaohongshu.com+{query}&num={max_results}"
        async with httpx.AsyncClient(timeout=15.0, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }) as client:
            resp = await client.get(search_url)
            results = []
            # Simple extraction from search results
            import re
            pattern = r'href="(https://www\.xiaohongshu\.com/[^"]+)"'
            matches = re.findall(pattern, resp.text)
            for url in matches[:max_results]:
                results.append({"url": url, "platform": platform, "query": query})
            return results
    except Exception as e:
        logger.warning(f"搜索失败: {e}")
        return []


async def crawl_posts_by_keywords(db: Session, keyword_group_id: int, keywords: list, exclude_keywords: list = None, max_posts: int = 10):
    """根据关键词采集帖子并分类保存"""
    crawl_log = CrawlLog(
        keyword_group_id=keyword_group_id,
        status="running",
        started_at=datetime.now(),
    )
    db.add(crawl_log)
    db.commit()

    total_new_leads = 0
    total_found = 0

    try:
        for keyword in keywords[:1]:  # Limit keywords to avoid rate limits
            # Search for posts
            search_results = await search_posts_from_web(keyword, max_results=max_posts)

            for result in search_results[:1]:  # Process 1 post per keyword for demo
                try:
                    # Fetch post content via web_fetch
                    content_data = await fetch_post_content(result["url"])
                    if not content_data:
                        continue

                    # Save post
                    post = Post(
                        platform="xiaohongshu",
                        platform_post_id=content_data.get("id", f"generated_{datetime.now().timestamp()}"),
                        title=content_data.get("title", ""),
                        content=content_data.get("content", ""),
                        author=content_data.get("author", "小红书用户"),
                        author_avatar=content_data.get("author_avatar", ""),
                        published_at=datetime.now(),
                        permalink=result["url"],
                        keyword_group_id=keyword_group_id,
                    )
                    db.add(post)
                    db.commit()
                    db.refresh(post)

                    # Save comments if any
                    for comment_data in content_data.get("comments", []):
                        comment = Comment(
                            post_id=post.id,
                            author=comment_data.get("author", ""),
                            content=comment_data.get("content", ""),
                            published_at=datetime.now(),
                        )
                        db.add(comment)
                    db.commit()

                    # LLM classification
                    comments_text = " ".join([c.get("content", "") for c in content_data.get("comments", [])])
                    classification = await classify_lead(
                        title=post.title or "",
                        content=post.content or "",
                        comments_text=comments_text
                    )

                    if classification.get("is_valid"):
                        existing_lead = db.query(Lead).filter(Lead.post_id == post.id).first()
                        if not existing_lead:
                            lead = Lead(
                                post_id=post.id,
                                lead_type=classification.get("lead_type", "无效"),
                                confidence=classification.get("confidence", 0),
                                reason=classification.get("reason", ""),
                                status="新线索",
                            )
                            db.add(lead)
                            total_new_leads += 1

                    total_found += 1
                    db.commit()

                except Exception as e:
                    logger.error(f"处理帖子失败: {e}")
                    continue

        crawl_log.status = "success"
        crawl_log.total_found = total_found
        crawl_log.new_leads = total_new_leads
        crawl_log.finished_at = datetime.now()
        db.commit()

    except Exception as e:
        crawl_log.status = "failed"
        crawl_log.error_message = str(e)
        crawl_log.finished_at = datetime.now()
        db.commit()
        logger.error(f"采集失败: {e}")

    return {"total_found": total_found, "new_leads": total_new_leads}


async def fetch_post_content(url: str) -> Optional[dict]:
    """获取帖子内容"""
    try:
        async with httpx.AsyncClient(timeout=15.0, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }) as client:
            resp = await client.get(url)
            if resp.status_code != 200:
                return None

            text = resp.text
            content = {}

            # Extract title
            import re
            title_match = re.search(r'<title[^>]*>(.*?)</title>', text, re.DOTALL)
            if title_match:
                content["title"] = title_match.group(1).strip()

            # Try to extract content
            body_match = re.search(r'<body[^>]*>(.*?)</body>', text, re.DOTALL)
            if body_match:
                body_text = body_match.group(1)
                # Remove script/style tags
                body_text = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', body_text, flags=re.DOTALL)
                # Remove HTML tags
                body_text = re.sub(r'<[^>]+>', '', body_text)
                body_text = re.sub(r'\s+', ' ', body_text)
                content["content"] = body_text[:1000].strip()
            else:
                content["content"] = text[:1000]

            if not content.get("title"):
                content["title"] = content.get("content", "")[:100]

            content["id"] = url.split("/")[-1] if "/" in url else str(hash(url))
            content["author"] = "小红书用户"
            content["comments"] = []
            return content

    except Exception as e:
        logger.warning(f"获取帖子内容失败: {e}")
        return None
