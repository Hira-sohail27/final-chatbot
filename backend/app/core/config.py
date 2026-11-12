from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db: str = "chatbot"
    qdrant_url: str = ""          # empty = use local file storage (no server/account needed)
    qdrant_path: str = "./qdrant_data"
    qdrant_api_key: str | None = None
    qdrant_collection: str = "knowledge_base"
    llm_api_key: str = ""
    llm_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/"
    chat_model: str = "gemini-2.5-flash"
    embed_model: str = "gemini-embedding-001"
    embed_dim: int = 3072
    jwt_secret: str = "change-me"
    jwt_expire_minutes: int = 1440
    cors_origin: str = "http://localhost:5173"
    rag_min_score: float = 0.55

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
