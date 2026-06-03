"""
Retrieval Module - Vector and keyword-based search with metadata filtering
Implements Use Case 3 requirement: department-level access control
"""

import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class RetrievalResult:
    """Result from a retrieval query"""
    text: str
    score: float
    metadata: Dict[str, Any]
    source: str


class VectorRetrieval:
    """Vector similarity-based retrieval"""

    def __init__(self, vector_store):
        """
        Initialize vector retrieval

        Args:
            vector_store: Vector database instance (ChromaDB, Pinecone, etc.)
        """
        self.vector_store = vector_store

    async def search(
        self,
        query_embedding: List[float],
        filters: Dict[str, Any],
        top_k: int = 5
    ) -> List[RetrievalResult]:
        """
        Search using vector similarity with department filtering

        CRITICAL: Use Case 3 Requirement - Department-level access control
        Filters are applied at vector DB level to ensure strict data separation

        Args:
            query_embedding: Query embedding vector
            filters: Metadata filters (must include 'department')
            top_k: Number of results to return

        Returns:
            List of RetrievalResult objects ranked by score
        """
        try:
            # Validate department filter (mandatory for Use Case 3)
            if not filters.get('department'):
                raise ValueError("Department filter is mandatory for secure access control")

            # Query vector store with filters
            results = await self.vector_store.query(
                query_embedding=query_embedding,
                filters=filters,
                top_k=top_k
            )

            # Transform results to RetrievalResult format
            retrieval_results = [
                RetrievalResult(
                    text=result['text'],
                    score=result['score'],
                    metadata=result['metadata'],
                    source=result['metadata'].get('document_name', 'Unknown')
                )
                for result in results
            ]

            return retrieval_results

        except Exception as e:
            print(f"❌ Vector retrieval failed: {str(e)}")
            raise


class KeywordRetrieval:
    """BM25-based keyword search for exact term matching"""

    def __init__(self, documents_db):
        """
        Initialize keyword retrieval

        Args:
            documents_db: Document database instance
        """
        self.documents_db = documents_db

    async def search(
        self,
        query: str,
        filters: Dict[str, Any],
        top_k: int = 5
    ) -> List[RetrievalResult]:
        """
        Search using keyword matching with BM25 scoring

        Args:
            query: Search query text
            filters: Metadata filters (department, category, etc.)
            top_k: Number of results to return

        Returns:
            List of RetrievalResult objects
        """
        try:
            # Validate department filter
            if not filters.get('department'):
                raise ValueError("Department filter is mandatory")

            # Tokenize query
            query_tokens = self._tokenize(query)

            # Get all documents matching department filter
            documents = await self.documents_db.get_by_filter(filters)

            # Score documents using BM25
            scored_docs = []
            for doc in documents:
                score = self._bm25_score(query_tokens, doc['text'])
                if score > 0:  # Only include documents with match
                    scored_docs.append({
                        'text': doc['text'],
                        'score': score,
                        'metadata': doc['metadata'],
                        'source': doc['metadata'].get('document_name', 'Unknown')
                    })

            # Sort by score and return top_k
            scored_docs.sort(key=lambda x: x['score'], reverse=True)
            top_results = scored_docs[:top_k]

            return [
                RetrievalResult(
                    text=result['text'],
                    score=result['score'],
                    metadata=result['metadata'],
                    source=result['source']
                )
                for result in top_results
            ]

        except Exception as e:
            print(f"❌ Keyword retrieval failed: {str(e)}")
            raise

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        """Tokenize text into lowercase words"""
        return text.lower().split()

    @staticmethod
    def _bm25_score(query_tokens: List[str], document: str) -> float:
        """
        Simple BM25-like scoring

        Args:
            query_tokens: Query tokens
            document: Document text

        Returns:
            BM25 score (higher = better match)
        """
        # Simple implementation: count matching tokens
        doc_tokens = document.lower().split()
        matches = sum(1 for token in query_tokens if token in doc_tokens)

        # Avoid division by zero and scale score
        if len(doc_tokens) == 0:
            return 0

        # TF-IDF-like scoring
        return (matches * 100) / len(doc_tokens)


class HybridRetrieval:
    """Combines vector and keyword search for robust retrieval"""

    def __init__(self, vector_retrieval: VectorRetrieval, keyword_retrieval: KeywordRetrieval):
        """
        Initialize hybrid retrieval

        Args:
            vector_retrieval: Vector retrieval instance
            keyword_retrieval: Keyword retrieval instance
        """
        self.vector_retrieval = vector_retrieval
        self.keyword_retrieval = keyword_retrieval

    async def search(
        self,
        query: str,
        query_embedding: List[float],
        filters: Dict[str, Any],
        top_k: int = 5,
        vector_weight: float = 0.7,
        keyword_weight: float = 0.3
    ) -> List[RetrievalResult]:
        """
        Search using both vector and keyword methods, combining results

        Args:
            query: Search query text
            query_embedding: Query embedding vector
            filters: Metadata filters
            top_k: Number of results to return
            vector_weight: Weight for vector similarity (0-1)
            keyword_weight: Weight for keyword matching (0-1)

        Returns:
            List of combined and ranked RetrievalResult objects
        """
        try:
            # Get results from both retrieval methods
            vector_results = await self.vector_retrieval.search(
                query_embedding, filters, top_k=top_k
            )
            keyword_results = await self.keyword_retrieval.search(
                query, filters, top_k=top_k
            )

            # Combine and re-rank results
            combined = self._combine_results(
                vector_results,
                keyword_results,
                vector_weight,
                keyword_weight
            )

            # Return top_k combined results
            return combined[:top_k]

        except Exception as e:
            print(f"❌ Hybrid retrieval failed: {str(e)}")
            raise

    @staticmethod
    def _combine_results(
        vector_results: List[RetrievalResult],
        keyword_results: List[RetrievalResult],
        vector_weight: float,
        keyword_weight: float
    ) -> List[RetrievalResult]:
        """
        Combine vector and keyword results using weighted scoring

        Args:
            vector_results: Results from vector search
            keyword_results: Results from keyword search
            vector_weight: Weight for vector scores
            keyword_weight: Weight for keyword scores

        Returns:
            Combined and re-ranked results
        """
        # Create score map for both result sets
        scores = {}

        # Add vector scores
        for result in vector_results:
            key = result.text[:100]  # Use text prefix as key
            scores[key] = {
                'result': result,
                'vector_score': result.score,
                'keyword_score': 0
            }

        # Add keyword scores
        for result in keyword_results:
            key = result.text[:100]
            if key in scores:
                scores[key]['keyword_score'] = result.score
            else:
                scores[key] = {
                    'result': result,
                    'vector_score': 0,
                    'keyword_score': result.score
                }

        # Calculate combined scores
        combined = []
        for key, score_data in scores.items():
            combined_score = (
                score_data['vector_score'] * vector_weight +
                score_data['keyword_score'] * keyword_weight
            )
            result = score_data['result']
            result.score = combined_score
            combined.append(result)

        # Sort by combined score
        combined.sort(key=lambda x: x.score, reverse=True)
        return combined
