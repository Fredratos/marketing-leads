"""初始化种子数据"""
from app.database import SessionLocal, init_db
from app.models.database import User, KeywordGroup
from app.auth import hash_password

def seed():
    init_db()
    db = SessionLocal()

    # Create admin user
    existing = db.query(User).filter(User.email == "admin@marketing-leads.com").first()
    if not existing:
        user = User(
            email="admin@marketing-leads.com",
            hashed_password=hash_password("admin123"),
            nickname="管理员",
            role="admin",
        )
        db.add(user)
        db.commit()
        print("✅ Admin user created: admin@marketing-leads.com / admin123")

    # Create default keyword groups
    if db.query(KeywordGroup).count() == 0:
        groups = [
            KeywordGroup(
                name="海外达人营销",
                keywords=["海外达人", "海外KOL", "海外红人营销", "海外达人合作"],
                platform="xiaohongshu",
            ),
            KeywordGroup(
                name="海外品牌出海",
                keywords=["海外品牌营销", "品牌出海", "出海营销", "海外推广"],
                platform="xiaohongshu",
            ),
            KeywordGroup(
                name="海外广告投流",
                keywords=["海外广告投放", "TikTok投流", "Facebook广告"],
                platform="xiaohongshu",
            ),
            KeywordGroup(
                name="找海外资源",
                keywords=["求推荐海外", "找海外达人", "海外MCN", "海外营销服务"],
                platform="xiaohongshu",
            ),
        ]
        for g in groups:
            db.add(g)
        db.commit()
        print(f"✅ Created {len(groups)} keyword groups")

    db.close()
    print("✅ Seed complete")


if __name__ == "__main__":
    seed()
