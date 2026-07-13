"""状态栏路由"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, Dict

from ..services.status_sheet import (
    render_status_html,
    render_status_text,
    generate_status_data,
    get_presets,
    PRESETS,
)

router = APIRouter(prefix="/api/status-sheet", tags=["status-sheet"])


class StatusDataRequest(BaseModel):
    """状态数据请求"""
    data: Dict[str, object]
    preset: str = "default"


class StatusGenerateRequest(BaseModel):
    """AI生成状态数据请求"""
    character_name: str
    context: str = ""
    preset: str = "default"


class StatusPreviewRequest(BaseModel):
    """状态预览请求"""
    data: Dict[str, object]
    preset: str = "default"
    format: str = "html"  # html / text


@router.get("/presets")
async def api_get_presets():
    """获取状态栏预设列表"""
    return {"status": "ok", "presets": get_presets()}


@router.post("/render")
async def api_render_status(req: StatusDataRequest):
    """渲染状态栏"""
    if req.preset not in PRESETS:
        raise HTTPException(status_code=400, detail=f"未知预设: {req.preset}")

    html = render_status_html(req.data, req.preset)
    text = render_status_text(req.data, req.preset)

    return {
        "status": "ok",
        "html": html,
        "text": text,
        "preset": req.preset,
    }


@router.post("/preview", response_class=HTMLResponse)
async def api_preview_status(req: StatusPreviewRequest):
    """状态栏预览（返回可渲染的HTML页面）"""
    if req.preset not in PRESETS:
        raise HTTPException(status_code=400, detail=f"未知预设: {req.preset}")

    html_content = render_status_html(req.data, req.preset)

    page = f"""<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <title>状态栏预览</title>
    <style>
        body {{ background: #1a1a2e; color: #e0e0e0; font-family: 'Microsoft YaHei', sans-serif; display: flex; justify-content: center; padding: 40px; }}
        .status-sheet {{ background: #16213e; border: 1px solid #0f3460; border-radius: 12px; padding: 20px 30px; min-width: 300px; box-shadow: 0 4px 20px rgba(0,0,0,0.5); }}
        .status-title {{ text-align: center; font-size: 18px; font-weight: bold; color: #e94560; margin-bottom: 15px; border-bottom: 1px solid #0f3460; padding-bottom: 10px; }}
        .status-row {{ display: flex; justify-content: space-between; align-items: center; padding: 6px 0; }}
        .label {{ color: #a0a0a0; min-width: 80px; }}
        .bar {{ font-family: monospace; color: #4ecca3; letter-spacing: 1px; }}
        .emoji {{ font-size: 20px; }}
        .value {{ color: #4ecca3; font-weight: bold; }}
        .text {{ color: #e0e0e0; }}
    </style>
</head>
<body>
    {html_content}
</body>
</html>"""
    return HTMLResponse(content=page)


@router.post("/generate")
async def api_generate_status(req: StatusGenerateRequest):
    """AI生成角色状态数据"""
    try:
        data = await generate_status_data(req.character_name, req.context)
        html = render_status_html(data, req.preset)
        text = render_status_text(data, req.preset)
        return {
            "status": "ok",
            "data": data,
            "html": html,
            "text": text,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
