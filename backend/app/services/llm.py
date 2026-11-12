import asyncio
import httpx
from app.core.config import settings

# Native Gemini REST API (works with the new "AQ." keys)
BASE = "https://generativelanguage.googleapis.com/v1beta"
# Used automatically if the main chat model is overloaded (503/429) or unavailable (404)
FALLBACK_MODELS = ["gemini-3.1-flash-lite", "gemini-3.5-flash", "gemini-flash-latest", "gemini-flash-lite-latest"]


class GeminiError(RuntimeError):
    def __init__(self, status: int, text: str):
        super().__init__(f"Gemini API error {status}: {text}")
        self.status = status


def _name(model: str) -> str:
    return model.strip().strip("\"'").removeprefix("models/").strip()


async def _post(path: str, body: dict, timeout: float = 30) -> dict:
    headers = {"x-goog-api-key": settings.llm_api_key, "Content-Type": "application/json"}
    async with httpx.AsyncClient(timeout=timeout) as client:
        r = await client.post(f"{BASE}/{path}", headers=headers, json=body)
    if r.status_code >= 400:
        raise GeminiError(r.status_code, r.text[:300])
    return r.json()


async def _post_retry(path: str, body: dict, attempts: int = 3) -> dict:
    last: Exception | None = None
    for i in range(attempts):
        try:
            return await _post(path, body)
        except GeminiError as e:
            last = e
            if e.status not in (429, 500, 503, 504):
                raise
        except httpx.HTTPError as e:
            last = e
        await asyncio.sleep(1.5 * (i + 1))
    raise last


async def embed(text: str) -> list[float]:
    m = _name(settings.embed_model)
    d = await _post_retry(f"models/{m}:embedContent", {"model": f"models/{m}", "content": {"parts": [{"text": text}]}})
    return d["embedding"]["values"]


async def embed_many(texts: list[str]) -> list[list[float]]:
    m = _name(settings.embed_model)
    reqs = [{"model": f"models/{m}", "content": {"parts": [{"text": t}]}} for t in texts]
    d = await _post_retry(f"models/{m}:batchEmbedContents", {"requests": reqs})
    return [e["values"] for e in d["embeddings"]]


async def complete(messages: list[dict]) -> str:
    system = "\n".join(m["content"] for m in messages if m["role"] == "system")
    contents = [{"role": "model" if m["role"] == "assistant" else "user", "parts": [{"text": m["content"]}]}
                for m in messages if m["role"] != "system"]
    body = {"contents": contents, "generationConfig": {"temperature": 0.2}}
    if system:
        body["systemInstruction"] = {"parts": [{"text": system}]}

    main = _name(settings.chat_model)
    models = [main] + [m for m in FALLBACK_MODELS if m != main]
    last: Exception | None = None
    for model in models[:4]:
        for attempt in range(2):
            try:
                d = await _post(f"models/{model}:generateContent", body)
                return d["candidates"][0]["content"]["parts"][0]["text"]
            except GeminiError as e:
                last = e
                if e.status in (401, 403):
                    raise                      # key problem: other models will not help
                if e.status in (429, 500, 503, 504) and attempt == 0:
                    await asyncio.sleep(1.5)   # overloaded: retry the same model once
                    continue
                break                          # 400/404/still overloaded: try the next model
            except httpx.HTTPError as e:       # timeout / network
                last = e
                break
            except (KeyError, IndexError):
                last = RuntimeError("Gemini returned an empty answer")
                break
    raise last or RuntimeError("No chat model available")