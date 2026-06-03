"""
Embeddings Module - Generate dense vector representations for documents and queries
Uses OpenAI's embedding model for semantic understanding
"""

import os
from typing import List
import openai

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY", "")
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSION = 1536


class EmbeddingGenerator:
    """Generate embeddings for text chunks"""

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

            # Use OpenAI API to generate embedding
            response = openai.Embedding.create(
                input=text,
                model=EMBEDDING_MODEL
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

            # OpenAI API handles batching efficiently
            response = openai.Embedding.create(
                input=texts,
                model=EMBEDDING_MODEL
            )

            # Sort by index to maintain order
            embeddings = sorted(response['data'], key=lambda x: x['index'])
            return [item['embedding'] for item in embeddings]

        except Exception as e:
            print(f"❌ Batch embedding generation failed: {str(e)}")
            raise
