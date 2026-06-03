"""Embeddings - Using local Hugging Face models (sentence-transformers)"""

import os
from typing import List
from pathlib import Path
from dotenv import load_dotenv

# Load .env
load_dotenv(Path.cwd() / ".env")

try:
    from sentence_transformers import SentenceTransformer
    
    # Use local sentence-transformers model
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION = 384
    
    # Load model once at import time
    _model = SentenceTransformer(EMBEDDING_MODEL)
    
except ImportError:
    raise ValueError("sentence-transformers not installed. Run: pip install sentence-transformers")


class EmbeddingGenerator:
    """Generate embeddings using local Hugging Face models"""

    @staticmethod
    async def generate_embedding(text: str) -> List[float]:
        """Generate embedding using local model"""
        if not text or not text.strip():
            raise ValueError("Cannot embed empty text")
        
        embedding = _model.encode(text, convert_to_tensor=False)
        return embedding.tolist()

    @staticmethod
    async def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
        """Generate embeddings batch using local model"""
        if not texts:
            raise ValueError("Cannot embed empty list")
        
        embeddings = _model.encode(texts, convert_to_tensor=False)
        return [e.tolist() for e in embeddings]
