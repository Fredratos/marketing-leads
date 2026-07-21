"""LLM 服务 - 使用 DeepSeek 进行智能线索识别"""
import json
import httpx
from loguru import logger
from app.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL

LEAD_CLASSIFICATION_PROMPT = """你是一个海外营销线索识别专家。你需要判断小红书帖子/评论是否是有价值的海外营销线索，并进行分类。

线索类型定义：
1. "找资源" - 帖子明确表达了在寻找海外达人/海外营销服务商/海外MCN合作资源的需求
2. "咨询求助" - 发帖询问海外品牌营销、海外达人合作、海外推广相关问题，表现出学习/求助意图
3. "经验分享" - 分享海外营销案例、方法论、ROI复盘、踩坑经验等有价值的内容
4. "资源展示" - MCN/代理商/服务商展示自己的海外达人资源和成功案例
5. "无效" - 与海外营销无关、纯广告无实质内容、或无法判断的内容

判断标准（非常重要）：
- 帖子核心主题必须与【海外品牌营销】【海外达人营销】【出海营销】直接相关
- 必须看发帖意图：是在【找人/找资源】还是在【分享经验】还是在【展示自己】
- 如果帖子只是提到"营销"但没有"海外/出海"语境，判为无效
- 如果只是国内营销内容，判为无效
- 广告贴如果没有实质性海外营销内容，判为无效

输入格式：
- 帖子标题 + 正文内容（可能包含评论）
- 平台：小红书

请返回严格JSON格式（不要包含markdown代码块标记）：
{"is_valid": true/false, "lead_type": "找资源|咨询求助|经验分享|资源展示|无效", "confidence": 0.0-1.0, "reason": "简短判断理由"}
"""


async def classify_lead(title: str, content: str, comments_text: str = "") -> dict:
    """使用 DeepSeek 进行线索识别"""
    full_text = f"标题：{title}\n内容：{content[:800]}\n评论摘要：{comments_text[:500]}"
    
    prompt = f"{LEAD_CLASSIFICATION_PROMPT}\n\n请判断以下帖子：\n{full_text}"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{DEEPSEEK_BASE_URL}/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": DEEPSEEK_MODEL,
                    "messages": [
                        {"role": "system", "content": "你是一个精准的海外营销线索分类器。只返回严格JSON格式，不要任何额外文字。"},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 256
                }
            )
            resp.raise_for_status()
            data = resp.json()
            result_text = data["choices"][0]["message"]["content"].strip()
            
            # Clean up markdown code blocks if present
            if result_text.startswith("```"):
                result_text = result_text.split("\n", 1)[1]
                if result_text.endswith("```"):
                    result_text = result_text[:-3]
                result_text = result_text.strip()
                if result_text.startswith("json"):
                    result_text = result_text[4:].strip()
            
            result = json.loads(result_text)
            logger.info(f"DeepSeek classify: {title[:30]}... -> {result.get('lead_type')} ({result.get('confidence')})")
            return result
            
    except Exception as e:
        logger.error(f"DeepSeek classify error: {e}")
        return {"is_valid": False, "lead_type": "无效", "confidence": 0.0, "reason": f"分类失败: {str(e)}"}
