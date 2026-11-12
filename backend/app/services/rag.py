from app.core.config import settings
from app.db.qdrant import qdrant
from app.services import llm

SYSTEM = (
    "You are a helpful assistant. Answer factual questions ONLY using the provided context. "
    "If the context is empty or does not contain the answer, reply that you cannot find a supported "
    "answer in the knowledge base. Never invent facts. Greetings and small talk are fine."
)


async def retrieve(query: str) -> list[dict]:
    vec = await llm.embed(query)
    res = await qdrant.query_points(settings.qdrant_collection, query=vec, limit=4,
                                    score_threshold=settings.rag_min_score, with_payload=True)
    return [{"source": p.payload.get("source"), "chunk_id": p.payload.get("chunk_id"),
             "text": p.payload.get("text", ""), "score": round(p.score, 3)} for p in res.points]


async def answer(query: str, history: list[dict]):
    chunks = await retrieve(query)
    ctx = "\n\n".join(f"[{c['source']}#{c['chunk_id']}] {c['text']}" for c in chunks) or "(no relevant context found)"
    msgs = [{"role": "system", "content": f"{SYSTEM}\n\nContext:\n{ctx}"}, *history,
            {"role": "user", "content": query}]
    text = await llm.complete(msgs)
    return text, [{"source": c["source"], "chunk_id": c["chunk_id"], "score": c["score"]} for c in chunks]
