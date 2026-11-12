"""Prints the Gemini models your key can use. Run from backend/: python -m scripts.list_models"""
import asyncio
import httpx
from app.core.config import settings


async def main():
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.get("https://generativelanguage.googleapis.com/v1beta/models",
                             headers={"x-goog-api-key": settings.llm_api_key}, params={"pageSize": 200})
    if r.status_code >= 400:
        print("ERROR", r.status_code, r.text[:300])
        return
    for m in r.json().get("models", []):
        methods = m.get("supportedGenerationMethods", [])
        kind = "CHAT " if "generateContent" in methods else "EMBED" if "embedContent" in methods else None
        if kind:
            print(kind, m["name"].removeprefix("models/"))


asyncio.run(main())