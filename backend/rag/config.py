import os

class RAGConfig:
    chunk_size = int(os.getenv("CHUNK_SIZE", "1000"))
    chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "200"))
    top_k_retrieval = int(os.getenv("TOP_K_RETRIEVAL", "5"))
    similarity_threshold = float(os.getenv("SIMILARITY_THRESHOLD", "0.5"))
    use_hybrid_search = os.getenv("USE_HYBRID_SEARCH", "true").lower() == "true"
    use_reranking = os.getenv("USE_RERANKING", "true").lower() == "true"
    embeddings_model = os.getenv("EMBEDDINGS_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

rag_config = RAGConfig()
