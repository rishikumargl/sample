"""
Vector Store Module - ChromaDB integration for document storage and retrieval
Provides persistent vector database with metadata filtering
"""

import os
import chromadb
from typing import List, Dict, Any, Optional
from chromadb.config import Settings


class ChromaVectorStore:
    """ChromaDB-based vector store for enterprise knowledge"""

    def __init__(self, persist_dir: Optional[str] = None):
        """
        Initialize ChromaDB vector store

        Args:
            persist_dir: Directory to persist data (None = in-memory)
        """
        # Use persistent storage if directory provided
        if persist_dir:
            settings = Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=persist_dir,
                anonymized_telemetry=False,
            )
            self.client = chromadb.Client(settings)
        else:
            self.client = chromadb.Client()

        # Create or get collection for enterprise documents
        self.collection = self.client.get_or_create_collection(
            name="enterprise_knowledge",
            metadata={"hnsw:space": "cosine"}
        )

        print(f"✓ Vector store initialized: {self.collection.name}")

    async def add_documents(
        self,
        chunks: List[Dict[str, Any]],
        embeddings: List[List[float]]
    ) -> int:
        """
        Add documents with embeddings to vector store

        Args:
            chunks: List of chunk objects with text and metadata
            embeddings: List of embedding vectors

        Returns:
            Number of documents added
        """
        try:
            if len(chunks) != len(embeddings):
                raise ValueError("Number of chunks must match number of embeddings")

            # Prepare data for ChromaDB
            ids = []
            documents = []
            metadatas = []

            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                # Create unique ID
                doc_name = chunk.get('metadata', {}).get('document_name', 'unknown')
                chunk_idx = chunk.get('chunk_index', 0)
                chunk_id = f"{doc_name}_{chunk_idx}_{i}".replace(" ", "_")

                ids.append(chunk_id)
                documents.append(chunk.get('text', ''))

                # Prepare metadata (ChromaDB filters use metadata)
                metadata = chunk.get('metadata', {})
                metadatas.append({
                    'department': metadata.get('department', 'unknown'),
                    'category': metadata.get('category', 'general'),
                    'document_name': metadata.get('document_name', 'unknown'),
                    'version': str(metadata.get('version', 1)),
                    'date': metadata.get('date', ''),
                    'chunk_index': str(chunk_idx),
                })

            # Add to collection with embeddings
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )

            print(f"✓ Added {len(chunks)} documents to vector store")
            return len(chunks)

        except Exception as e:
            print(f"❌ Failed to add documents: {str(e)}")
            raise

    async def query(
        self,
        query_embedding: List[float],
        filters: Optional[Dict[str, Any]] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Query vector store with metadata filtering

        CRITICAL: Use Case 3 Requirement - Department filtering
        Ensures strict department-level access control

        Args:
            query_embedding: Query embedding vector
            filters: Metadata filters (e.g., {'department': 'engineering'})
            top_k: Number of results to return

        Returns:
            List of result dictionaries with text, score, and metadata
        """
        try:
            # Build where filter for ChromaDB
            where_filter = None
            if filters:
                if not filters.get('department'):
                    raise ValueError("Department filter is mandatory")

                # Create metadata filter for ChromaDB
                where_filter = {
                    '$and': [
                        {'department': {'$eq': filters['department'].lower()}}
                    ]
                }

                # Add optional category filter
                if filters.get('category'):
                    where_filter['$and'].append({
                        'category': {'$eq': filters['category'].lower()}
                    })

            # Query collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where_filter,
                include=['embeddings', 'documents', 'metadatas', 'distances']
            )

            # Transform results
            transformed_results = []
            if results['ids'] and len(results['ids']) > 0:
                for i, doc_id in enumerate(results['ids'][0]):
                    # ChromaDB returns distances; convert to similarity scores (0-1)
                    # For cosine distance: similarity = 1 - distance
                    distance = results['distances'][0][i] if i < len(results['distances'][0]) else 0
                    score = 1 - distance if distance <= 1 else 0

                    metadata = results['metadatas'][0][i] if i < len(results['metadatas'][0]) else {}

                    transformed_results.append({
                        'id': doc_id,
                        'text': results['documents'][0][i] if i < len(results['documents'][0]) else '',
                        'score': score,
                        'metadata': {
                            'department': metadata.get('department', 'unknown'),
                            'category': metadata.get('category', 'general'),
                            'document_name': metadata.get('document_name', 'unknown'),
                            'version': int(metadata.get('version', 1)),
                            'date': metadata.get('date', ''),
                            'chunk_index': int(metadata.get('chunk_index', 0)),
                        }
                    })

            print(f"✓ Vector query returned {len(transformed_results)} results (department: {filters.get('department')})")
            return transformed_results

        except Exception as e:
            print(f"❌ Vector query failed: {str(e)}")
            raise

    async def delete_by_metadata(
        self,
        filters: Dict[str, Any]
    ) -> int:
        """
        Delete documents by metadata filter

        Args:
            filters: Metadata filters

        Returns:
            Number of documents deleted
        """
        try:
            # Build where filter
            where_filter = None
            if filters:
                where_filter = {
                    'department': {'$eq': filters['department'].lower()}
                }

                if filters.get('category'):
                    where_filter['$and'] = [
                        {'category': {'$eq': filters['category'].lower()}}
                    ]

            # Get IDs to delete
            results = self.collection.get(where=where_filter)
            ids_to_delete = results['ids']

            if ids_to_delete:
                self.collection.delete(ids=ids_to_delete)
                print(f"✓ Deleted {len(ids_to_delete)} documents")

            return len(ids_to_delete)

        except Exception as e:
            print(f"❌ Failed to delete by metadata: {str(e)}")
            raise

    async def get_stats(self) -> Dict[str, Any]:
        """
        Get vector store statistics

        Returns:
            Statistics dictionary
        """
        try:
            count = self.collection.count()
            return {
                'collection_name': self.collection.name,
                'document_count': count,
                'embedding_dimension': 1536  # OpenAI embedding dimension
            }
        except Exception as e:
            print(f"❌ Failed to get stats: {str(e)}")
            raise

    async def clear(self) -> None:
        """Clear all documents from collection"""
        try:
            # Delete collection and recreate
            self.client.delete_collection(name="enterprise_knowledge")
            self.collection = self.client.get_or_create_collection(
                name="enterprise_knowledge",
                metadata={"hnsw:space": "cosine"}
            )
            print("✓ Cleared vector store")
        except Exception as e:
            print(f"❌ Failed to clear vector store: {str(e)}")
            raise
