"""工具函数"""
import re
from datetime import datetime


def clean_html(html_text: str) -> str:
    """去除HTML标签"""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', html_text or "")


def truncate_text(text: str, max_len: int = 200) -> str:
    """截断文本"""
    if not text:
        return ""
    if len(text) <= max_len:
        return text
    return text[:max_len] + "..."


def parse_datetime_str(dt_str: str) -> datetime:
    """解析各种日期格式"""
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(dt_str, fmt)
        except ValueError:
            continue
    return datetime.now()
