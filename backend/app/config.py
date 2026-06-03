import os

class Settings:
    backend_host = os.getenv("BACKEND_HOST", "0.0.0.0")
    backend_port = int(os.getenv("BACKEND_PORT", "8000"))
    debug = os.getenv("DEBUG", "true").lower() == "true"
    database_url = os.getenv("DATABASE_URL", "sqlite:///./enterprise_rag.db")
    cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    openai_api_key = os.getenv("OPENAI_API_KEY", "")
    chunk_size = int(os.getenv("CHUNK_SIZE", "1000"))
    chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "200"))
    top_k_retrieval = int(os.getenv("TOP_K_RETRIEVAL", "5"))

settings = Settings()
