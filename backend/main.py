"""Nexus Free - 虚拟角色检索引擎"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(
    title="Nexus Free",
    description="虚拟角色检索引擎 - 免费开源版",
    version="0.2.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
from backend.routers import search, generate

app.include_router(search.router)
app.include_router(generate.router)


@app.get("/api/health")
async def health():
    """健康检查"""
    return {"status": "ok", "version": "0.2.0"}


@app.get("/", response_class=HTMLResponse)
async def root():
    """返回前端页面"""
    html_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Nexus Free</h1><p>前端页面未找到</p>")
