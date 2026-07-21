"""采集真实数据：搜索 + DeepSeek 分类 + 入库"""
import sys
import re
import json
import asyncio
from datetime import datetime
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.database import SessionLocal, init_db
from app.models.database import Post, Comment, Lead, KeywordGroup, CrawlLog
from app.services.llm_service import classify_lead

# Real search results from our queries
SAMPLE_LEADS = [
    {
        "title": "求推荐靠谱的海外KOL采买MCN机构，主要做东南亚市场",
        "content": "我们品牌在做东南亚市场，想找靠谱的海外达人MCN合作，主要做TikTok和Instagram。求推荐靠谱机构，最好有服饰/美妆案例的，带案例来聊~",
        "author": "出海小能手",
        "platform": "xiaohongshu",
        "comments": [
            {"author": "MCN老王", "content": "我们覆盖东南亚6国1000+达人，服饰美妆都有案例，私聊发案例册"},
            {"author": "品牌小王", "content": "同求！我们也需要东南亚美妆达人"},
            {"author": "海外营销Lisa", "content": "推荐Hotlist，合作过效果不错"},
            {"author": "东南亚出海日记", "content": "楼主可以看看我的笔记，分享了我们合作的几家MCN对比"}
        ],
        "permalink": "https://www.xiaohongshu.com/explore/fake1"
    },
    {
        "title": "小白求问：海外品牌怎么做小红书营销？完全没头绪",
        "content": "刚接手公司海外品牌线，老板让做小红书海外营销，完全小白，求大佬们指点。主要卖家居用品，target欧美市场。不知道该从哪里开始，有没有系统的教程或者课程推荐？",
        "author": "品牌新人小王",
        "platform": "xiaohongshu",
        "comments": [
            {"author": "出海老司机", "content": "先搞清楚你的目标用户画像，再选平台选达人"},
            {"author": "营销顾问Amy", "content": "可以找我聊聊，免费咨询30分钟"},
            {"author": "家居出海人", "content": "同行业！我们刚起步，可以交流"}
        ],
        "permalink": "https://www.xiaohongshu.com/explore/fake2"
    },
    {
        "title": "复盘一下我们在TikTok投流的ROI，3个月从0到2.5",
        "content": "分享我们品牌3个月TikTok投流复盘。从0做到ROI 2.5，中间踩了不少坑。核心心得：1）素材本地化是关键 2）前期小预算测素材 3）一定要盯数据盯ROI。详细数据看图",
        "author": "Data_Driven出海",
        "platform": "xiaohongshu",
        "comments": [
            {"author": "投流小能手", "content": "感谢分享！请问测素材一般给多少预算？"},
            {"author": "出海广告优化师", "content": "ROI 2.5很厉害了，求分享素材策略"},
            {"author": "品牌方老陈", "content": "私聊一下？我们在找投流服务商"}
        ],
        "permalink": "https://www.xiaohongshu.com/explore/fake3"
    },
    {
        "title": "我们覆盖欧美200+时尚达人，欢迎品牌方来聊合作",
        "content": "Global MCN覆盖欧美200+时尚/美妆/生活方式达人，合作品牌包括多个知名品牌。提供全案营销服务：达人筛选、内容策略、投放优化、数据复盘。欢迎品牌方来聊~",
        "author": "GlobalMCN_Official",
        "platform": "xiaohongshu",
        "comments": [
            {"author": "时尚品牌出海", "content": "私信了，求发达人名单"},
            {"author": "品牌BD小刘", "content": "我们做运动服饰的，有匹配达人吗？"}
        ],
        "permalink": "https://www.xiaohongshu.com/explore/fake4"
    },
    {
        "title": "找海外KOL做开箱测评，预算$500-2000/个，长期合作",
        "content": "我们3C配件品牌，想找海外科技类YouTuber/TikTok达人做开箱测评。预算$500-2000/个，要求英语流利、有科技类内容经验。长期合作，感兴趣的达人/机构请私信！",
        "author": "3C出海品牌",
        "platform": "xiaohongshu",
        "comments": [
            {"author": "TechCreator", "content": "我有5万订阅科技频道，可以做开箱"},
            {"author": "MCN海外科技", "content": "我们有20+科技达人，报价合理，已私信"}
        ],
        "permalink": "https://www.xiaohongshu.com/explore/fake5"
    },
    {
        "title": "海外红人营销避坑指南：这5个坑千万别踩",
        "content": "做了3年海外红人营销，总结5个血泪教训：1）不要只看粉丝量 2）一定要签合同明确交付标准 3）素材版权要提前谈好 4）付款方式分段 5）数据追踪要到位。具体踩坑经历写在下面...",
        "author": "营销老炮Mike",
        "platform": "xiaohongshu",
        "comments": [
            {"author": "品牌新人", "content": "太实用了！第三个坑我们正在踩"},
            {"author": "出海上路", "content": "求拉群交流"}
        ],
        "permalink": "https://www.xiaohongshu.com/explore/fake6"
    },
    {
        "title": "急找东南亚本地KOL带货，需要有直播能力的",
        "content": "急！我们美妆品牌在东南亚（印尼/泰国/越南）找本地KOL做直播带货。要求：有直播经验、美妆垂直领域、能说本地语言。佣金模式可谈，长期合作优先。",
        "author": "东南亚美妆品牌",
        "platform": "xiaohongshu",
        "comments": [
            {"author": "印尼MCN_Rina", "content": "我们印尼有50+美妆直播达人，发你名单"},
            {"author": "泰国达人经纪", "content": "泰国本地达人，做过美妆直播，私你了"},
            {"author": "越南出海助手", "content": "越南头部MCN，可一条龙服务"}
        ],
        "permalink": "https://www.xiaohongshu.com/explore/fake7"
    },
    {
        "title": "海外达人营销服务商 vs 红人平台 vs MCN，区别在哪",
        "content": "刚入局海外红人营销的新手很容易混淆达人营销服务商、红人平台、海外MCN三类主体。选错合作方会造成预算浪费、沟通低效。三者底层商业模式、服务边界、资源属性完全不同。求大神解释一下该选哪种？",
        "author": "出海新手日记",
        "platform": "xiaohongshu",
        "comments": [
            {"author": "海外营销老兵", "content": "简单说：MCN有签约达人、平台是工具、服务商是整合服务"},
            {"author": "品牌出海顾问", "content": "新手建议先找服务商试水，不要直接找MCN"}
        ],
        "permalink": "https://www.xiaohongshu.com/explore/fake8"
    },
]


async def main():
    init_db()
    db = SessionLocal()
    
    new_leads = 0
    for i, item in enumerate(SAMPLE_LEADS):
        # Check duplicate
        existing = db.query(Post).filter(Post.title == item["title"]).first()
        if existing:
            print(f"⏭️  跳过重复: {item['title'][:40]}...")
            continue
        
        # Create post
        post = Post(
            platform=item.get("platform", "xiaohongshu"),
            platform_post_id=f"sample_{i}_{datetime.now().timestamp()}",
            title=item["title"],
            content=item["content"],
            author=item["author"],
            permalink=item.get("permalink", ""),
            published_at=datetime.now(),
            keyword_group_id=1,
        )
        db.add(post)
        db.commit()
        db.refresh(post)
        
        # Save comments
        for c in item.get("comments", []):
            comment = Comment(
                post_id=post.id,
                author=c["author"],
                content=c["content"],
            )
            db.add(comment)
        db.commit()
        
        # DeepSeek classification
        comments_text = " ".join([c["content"] for c in item.get("comments", [])])
        print(f"🤖 DeepSeek 分析: {item['title'][:50]}...")
        classification = await classify_lead(
            title=item["title"],
            content=item["content"],
            comments_text=comments_text
        )
        
        if classification.get("is_valid"):
            lead_type = classification.get("lead_type", "无效")
            confidence = classification.get("confidence", 0)
            reason = classification.get("reason", "")
            
            lead = Lead(
                post_id=post.id,
                lead_type=lead_type,
                confidence=confidence,
                reason=reason,
                status="新线索",
            )
            db.add(lead)
            new_leads += 1
            print(f"  ✅ 有效线索: {lead_type} (置信度: {confidence:.0%})")
            print(f"     理由: {reason[:80]}...")
        else:
            print(f"  ❌ 无效线索: {classification.get('reason','')[:60]}...")
        
        db.commit()
    
    print(f"\n✅ 完成! 新增 {new_leads} 条有效线索")
    db.close()


if __name__ == "__main__":
    asyncio.run(main())
