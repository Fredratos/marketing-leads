"""FastAPI 应用入口 - 同时服务 API + 前端 SPA"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from pathlib import Path

from app.database import init_db
from app.api import auth, leads, keywords, crawl, stats


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="海外营销线索平台 API",
    description="多渠道营销线索平台 - DeepSeek 智能线索识别",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(auth.router)
app.include_router(leads.router)
app.include_router(keywords.router)
app.include_router(crawl.router)
app.include_router(stats.router)

# Static files - frontend SPA
static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "version": "0.1.0"}


@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    """Serve frontend SPA - all non-API routes return index.html"""
    index_path = static_dir / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"message": "Frontend not found. Place index.html in static/"}
