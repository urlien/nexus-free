"""LLM 服务 - 支持 Gemini 官方 API 与智谱 GLM (OpenAI兼容)"""
import os
import asyncio
import json
import httpx
from typing import Optional

# ===== 配置 =====
PROVIDER = os.getenv("LLM_PROVIDER", "zhipu")  # 默认智谱

# Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta/models"

# 智谱
ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY", "1d53cf994e3f433e9fe11380757a37f0.3d8XZTiIN3jpR67o")
ZHIPU_MODEL = os.getenv("ZHIPU_MODEL", "glm-4-flash")
ZHIPU_BASE = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

PROXY = os.getenv("HTTPS_PROXY") or os.getenv("HTTP_PROXY") or ""
RETRY_MAX = 3
RETRY_BASE_DELAY = 2.0


def _client() -> httpx.AsyncClient:
    kwargs = {"timeout": 120.0}
    if PROXY:
        kwargs["proxy"] = PROXY
    return httpx.AsyncClient(**kwargs)


async def _call_gemini(prompt: str, system: str, temperature: float, max_tokens: int, force_json: bool) -> str:
    url = f"{GEMINI_BASE}/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens},
    }
    if system:
        payload["systemInstruction"] = {"parts": [{"text": system}]}
    if force_json:
        payload["generationConfig"]["responseMimeType"] = "application/json"

    async with _client() as client:
        resp = await client.post(url, json=payload)
        if resp.status_code != 200:
            raise RuntimeError(f"Gemini HTTP {resp.status_code}: {resp.text[:200]}")
        data = resp.json()
        candidates = data.get("candidates") or []
        if not candidates:
            raise RuntimeError(f"Gemini 空响应: {data}")
        parts = candidates[0].get("content", {}).get("parts", [])
        return "".join(p.get("text", "") for p in parts).strip()


async def _call_zhipu(prompt: str, system: str, temperature: float, max_tokens: int, force_json: bool) -> str:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    
    payload = {
        "model": ZHIPU_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if force_json:
        payload["response_format"] = {"type": "json_object"}
        
    headers = {
        "Authorization": f"Bearer {ZHIPU_API_KEY}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient(timeout=120.0) as client:  # 智谱国内直连不需要代理
        resp = await client.post(ZHIPU_BASE, json=payload, headers=headers)
        if resp.status_code != 200:
            raise RuntimeError(f"Zhipu HTTP {resp.status_code}: {resp.text[:200]}")
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()


async def call_llm(
    prompt: str,
    system: str = "",
    model: Optional[str] = None,
    max_tokens: int = 8192,
    temperature: float = 0.7,
    force_json: bool = False,
) -> str:
    """统一入口，带自动重试"""
    last_err = None
    for attempt in range(RETRY_MAX):
        try:
            if PROVIDER == "gemini":
                return await _call_gemini(prompt, system, temperature, max_tokens, force_json)
            else:
                return await _call_zhipu(prompt, system, temperature, max_tokens, force_json)
        except (httpx.TimeoutException, httpx.ConnectError) as e:
            last_err = f"网络错误: {e}"
        except Exception as e:
            last_err = str(e)
        
        await asyncio.sleep(RETRY_BASE_DELAY * (2 ** attempt))
        
    raise RuntimeError(f"LLM 调用失败（已重试{RETRY_MAX}次）: {last_err}")


def _clean_json_text(raw: str) -> str:
    text = raw.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        inner = []
        in_block = False
        for line in lines:
            if line.startswith("```") and not in_block:
                in_block = True
                continue
            elif line.startswith("```") and in_block:
                break
            elif in_block:
                inner.append(line)
        text = "\n".join(inner).strip()
    return text


async def call_llm_json(
    prompt: str,
    system: str = "",
    model: Optional[str] = None,
    max_tokens: int = 8192,
) -> dict | list:
    raw = await call_llm(
        prompt=prompt,
        system=system,
        model=model,
        max_tokens=max_tokens,
        temperature=0.2,
        force_json=True,
    )
    text = _clean_json_text(raw)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        for l, r in (("{", "}"), ("[", "]")):
            i, j = text.find(l), text.rfind(r)
            if i != -1 and j != -1 and j > i:
                try:
                    return json.loads(text[i:j+1])
                except json.JSONDecodeError:
                    continue
        return {"error": "JSON解析失败", "raw": raw[:1000]}
