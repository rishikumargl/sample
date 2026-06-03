"""
Chunking Strategies Module - Split documents into retrievable chunks
Implements fixed-size and semantic chunking approaches
"""

import re
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class Chunk:
    """Represents a document chunk with metadata"""
    text: str
    metadata: Dict[str, Any]
    chunk_index: int


class FixedSizeChunking:
    """Fixed-size chunking with overlap for context preservation"""

    def __init__(self, chunk_size: int = 500, overlap: int = 100):
        """
        Initialize fixed-size chunker

        Args:
            chunk_size: Target size per chunk in characters (default 500)
            overlap: Overlap between consecutive chunks (default 100)
        """
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str, metadata: Dict[str, Any]) -> List[Chunk]:
        """
        Split text into fixed-size chunks with overlap

        Args:
            text: Text to chunk
            metadata: Document metadata

        Returns:
            List of Chunk objects
        """
        if not text or len(text.strip()) == 0:
            return []

        chunks = []
        chunk_index = 0
        position = 0

        while position < len(text):
            # Extract chunk of specified size
            chunk_end = min(position + self.chunk_size, len(text))
            chunk_text = text[position:chunk_end]

            # Create chunk object
            chunk = Chunk(
                text=chunk_text.strip(),
                metadata=metadata.copy(),
                chunk_index=chunk_index
            )
            chunks.append(chunk)

            # Move position with overlap
            position += self.chunk_size - self.overlap
            chunk_index += 1

        print(f"✓ Fixed-size chunking: {len(chunks)} chunks (size={self.chunk_size}, overlap={self.overlap})")
        return chunks


class SemanticChunking:
    """Semantic chunking based on sentence boundaries and coherence"""

    def __init__(self, target_chunk_size: int = 500, min_chunk_size: int = 50):
        """
        Initialize semantic chunker

        Args:
            target_chunk_size: Target size for chunks (default 500)
            min_chunk_size: Minimum size to consider a chunk valid (default 50)
        """
        self.target_chunk_size = target_chunk_size
        self.min_chunk_size = min_chunk_size

    def _split_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences using regex

        Args:
            text: Text to split into sentences

        Returns:
            List of sentences
        """
        # Handle common sentence delimiters
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    def chunk(self, text: str, metadata: Dict[str, Any]) -> List[Chunk]:
        """
        Split text into semantic chunks based on sentence boundaries

        Args:
            text: Text to chunk
            metadata: Document metadata

        Returns:
            List of Chunk objects
        """
        if not text or len(text.strip()) == 0:
            return []

        # Split into sentences
        sentences = self._split_sentences(text)

        if not sentences:
            return [Chunk(text=text, metadata=metadata.copy(), chunk_index=0)]

        chunks = []
        current_chunk = []
        current_size = 0
        chunk_index = 0

        for sentence in sentences:
            sentence_length = len(sentence)

            # If adding this sentence exceeds target size, finalize current chunk
            if current_size + sentence_length > self.target_chunk_size and current_chunk:
                chunk_text = " ".join(current_chunk)

                # Only create chunk if it meets minimum size requirement
                if len(chunk_text) >= self.min_chunk_size:
                    chunk = Chunk(
                        text=chunk_text,
                        metadata=metadata.copy(),
                        chunk_index=chunk_index
                    )
                    chunks.append(chunk)
                    chunk_index += 1

                current_chunk = []
                current_size = 0

            # Add sentence to current chunk
            current_chunk.append(sentence)
            current_size += sentence_length + 1  # +1 for space

        # Add remaining chunk if it has content
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            if len(chunk_text) >= self.min_chunk_size:
                chunk = Chunk(
                    text=chunk_text,
                    metadata=metadata.copy(),
                    chunk_index=chunk_index
                )
                chunks.append(chunk)

        print(f"✓ Semantic chunking: {len(chunks)} chunks (target_size={self.target_chunk_size})")
        return chunks


class HybridChunking:
    """Combines fixed-size and semantic chunking for optimal results"""

    def __init__(self, target_size: int = 500, overlap: int = 100):
        """
        Initialize hybrid chunker

        Args:
            target_size: Target chunk size
            overlap: Overlap between chunks
        """
        self.semantic_chunker = SemanticChunking(target_chunk_size=target_size)
        self.fixed_chunker = FixedSizeChunking(chunk_size=target_size, overlap=overlap)

    def chunk(self, text: str, metadata: Dict[str, Any], strategy: str = "semantic") -> List[Chunk]:
        """
        Chunk text using specified strategy

        Args:
            text: Text to chunk
            metadata: Document metadata
            strategy: 'semantic' or 'fixed'

        Returns:
            List of Chunk objects
        """
        if strategy == "semantic":
            return self.semantic_chunker.chunk(text, metadata)
        elif strategy == "fixed":
            return self.fixed_chunker.chunk(text, metadata)
        else:
            # Default to semantic
            return self.semantic_chunker.chunk(text, metadata)
