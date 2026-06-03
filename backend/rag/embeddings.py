"""
Embeddings Module - Generate dense vector representations for documents and queries
Uses Hugging Face sentence-transformers for semantic understanding (free & open-source)
"""

import os
from typing import List

# Try to use Hugging Face sentence-transformers (free)
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDING_METHOD = "huggingface"
except ImportError:
    EMBEDDING_METHOD = "openai"
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY", "")

# Configuration
HF_TOKEN = os.getenv("HF_TOKEN", "")
EMBEDDING_MODEL_HF = "sentence-transformers/all-MiniLM-L6-v2"  # Free, fast, 384-dim
EMBEDDING_MODEL_OPENAI = "text-embedding-3-small"
EMBEDDING_DIMENSION = 384 if EMBEDDING_METHOD == "huggingface" else 1536


class EmbeddingGenerator:
    """Generate embeddings for text chunks using Hugging Face or OpenAI"""

    _model = None  # Cache model to avoid reloading

    @classmethod
    def _get_model(cls):
        """Lazy load embedding model"""
        if cls._model is None:
            if EMBEDDING_METHOD == "huggingface":
                print(f"✓ Loading HuggingFace model: {EMBEDDING_MODEL_HF}")
                cls._model = SentenceTransformer(EMBEDDING_MODEL_HF)
            else:
                print(f"✓ Using OpenAI model: {EMBEDDING_MODEL_OPENAI}")
        return cls._model

    @staticmethod
    async def generate_embedding(text: str) -> List[float]:
        """
        Generate embedding vector for a text string

        Args:
            text: Text to embed

        Returns:
            List of floats representing the embedding vector
        """
        try:
            if not text or len(text.strip()) == 0:
                raise ValueError("Cannot embed empty text")

            if EMBEDDING_METHOD == "huggingface":
                # Use Hugging Face sentence-transformers (FREE!)
                model = EmbeddingGenerator._get_model()
                embedding = model.encode(text, convert_to_tensor=False)
                return embedding.tolist()

            else:
                # Fallback to OpenAI
                response = openai.Embedding.create(
                    input=text,
                    model=EMBEDDING_MODEL_OPENAI
                )
                embedding = response['data'][0]['embedding']
                return embedding

        except Exception as e:
            print(f"❌ Embedding generation failed: {str(e)}")
            raise

    @staticmethod
    async def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batch
        More efficient than individual API calls

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors
        """
        try:
            if not texts or len(texts) == 0:
                raise ValueError("Cannot embed empty list")

            if EMBEDDING_METHOD == "huggingface":
                # Use Hugging Face (batch processing - FREE!)
                model = EmbeddingGenerator._get_model()
                embeddings = model.encode(texts, convert_to_tensor=False)
                return [e.tolist() for e in embeddings]

            else:
                # Fallback to OpenAI batch
                response = openai.Embedding.create(
                    input=texts,
                    model=EMBEDDING_MODEL_OPENAI
                )
                embeddings = sorted(response['data'], key=lambda x: x['index'])
                return [item['embedding'] for item in embeddings]

        except Exception as e:
            print(f"❌ Batch embedding generation failed: {str(e)}")
            raise
