# Marketing Leads

多渠道营销线索平台 — 发现、筛选和管理多平台营销线索（小红书、抖音等）。

## 架构

- **后端**: Python FastAPI + PostgreSQL + Redis + Celery
- **前端**: React 18 + TypeScript + Ant Design 5
- **AI**: LLM 智能线索识别与分类

## 目录结构

```
marketing-leads/
├── backend/          # FastAPI 后端
│   ├── app/
│   │   ├── api/          # API 路由
│   │   ├── models/       # 数据库模型
│   │   ├── services/     # 业务逻辑
│   │   └── tasks/        # Celery 异步任务
│   └── requirements.txt
├── frontend/        # React 前端
│   └── src/
│       ├── components/  # 通用组件
│       ├── pages/      # 页面组件
│       ├── hooks/      # 自定义 hooks
│       └── utils/      # 工具函数
└── docs/           # 文档和原型
    ├── PRD.md
    ├── feature_list.md
    └── prototype.html
```

## 快速开始

### 后端

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 前端

```bash
cd frontend
npm install
npm run dev
```
