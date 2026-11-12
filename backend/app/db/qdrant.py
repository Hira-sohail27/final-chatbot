from qdrant_client import AsyncQdrantClient
from app.core.config import settings

# QDRANT_URL empty -> embedded local mode (data stored in a folder, no server or account needed)
if settings.qdrant_url:
    qdrant = AsyncQdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)
else:
    qdrant = AsyncQdrantClient(path=settings.qdrant_path)
