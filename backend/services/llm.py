"""LLM 服务 - MiMo API (OpenAI兼容)"""
import os
import httpx
import json
from typing import Optional

# API配置 - 优先从环境变量读取
API_BASE = os.getenv("MIMO_API_BASE", "https://token-plan-cn.xiaomimimo.com/v1")
API_KEY = os.getenv("MIMO_API_KEY", "")
MODEL = os.getenv("MIMO_MODEL", "mimo-flash")


async def call_llm(
    prompt: str,
    system: str = "",
    model: Optional[str] = None,
    max_tokens: int = 2000,
    temperature: float = 0.7,
) -> str:
    """调用 MiMo LLM API"""
    if not API_KEY:
        raise ValueError("未配置 MIMO_API_KEY 环境变量")

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            f"{API_BASE}/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": model or MODEL,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]


async def call_llm_json(
    prompt: str,
    system: str = "",
    model: Optional[str] = None,
) -> dict:
    """调用 LLM 并解析 JSON 返回"""
    raw = await call_llm(
        prompt=prompt,
        system=system,
        model=model,
        temperature=0.3,  # JSON 输出用低温度
    )
    # 尝试从 markdown code block 中提取 JSON
    text = raw.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        json_lines = []
        in_block = False
        for line in lines:
            if line.startswith("```") and not in_block:
                in_block = True
                continue
            elif line.startswith("```") and in_block:
                break
            elif in_block:
                json_lines.append(line)
        text = "\n".join(json_lines)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"raw": raw, "error": "JSON解析失败"}
