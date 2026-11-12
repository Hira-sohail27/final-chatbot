"""Index kb/*.txt into Qdrant. Run from backend/: python -m scripts.index_kb"""
import asyncio, pathlib, uuid
from qdrant_client.models import Distance, PointStruct, VectorParams
from app.core.config import settings
from app.db.qdrant import qdrant
from app.services.llm import embed_many


async def main():
    chunks = []
    for f in sorted(pathlib.Path("kb").glob("*.txt")):
        paras = [p.strip() for p in f.read_text(encoding="utf-8").split("\n\n") if p.strip()]
        chunks += [(f.stem, i, p) for i, p in enumerate(paras)]
    if not await qdrant.collection_exists(settings.qdrant_collection):
        await qdrant.create_collection(settings.qdrant_collection,
                                       vectors_config=VectorParams(size=settings.embed_dim, distance=Distance.COSINE))
    vecs = await embed_many([c[2] for c in chunks])
    pts = [PointStruct(id=str(uuid.uuid5(uuid.NAMESPACE_URL, f"{d}:{i}")), vector=v,
                       payload={"document_id": d, "chunk_id": i, "source": d, "text": t, "access": "public"})
           for (d, i, t), v in zip(chunks, vecs)]
    await qdrant.upsert(settings.qdrant_collection, pts)
    print(f"Indexed {len(pts)} chunks into '{settings.qdrant_collection}'")


asyncio.run(main())
