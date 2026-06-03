"""
Document Ingestion Module - Parse and chunk documents for RAG
Supports PDF, DOCX, Markdown, and plain text with metadata extraction
"""

import os
import PyPDF2
from typing import List, Dict, Any, Tuple
from datetime import datetime
from pathlib import Path
from dataclasses import asdict

from chunking_strategies import Chunk, FixedSizeChunking, SemanticChunking, HybridChunking


class DocumentParser:
    """Parse various document types and extract text"""

    @staticmethod
    def parse_pdf(file_path: str) -> str:
        """
        Parse PDF file and extract text

        Args:
            file_path: Path to PDF file

        Returns:
            Extracted text
        """
        try:
            text = []
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text.append(page.extract_text())

            result = "\n".join(text)
            print(f"✓ Parsed PDF: {file_path} ({len(result)} characters)")
            return result

        except Exception as e:
            print(f"❌ Failed to parse PDF: {str(e)}")
            raise

    @staticmethod
    def parse_docx(file_path: str) -> str:
        """
        Parse DOCX file and extract text

        Args:
            file_path: Path to DOCX file

        Returns:
            Extracted text
        """
        try:
            from docx import Document
            doc = Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            print(f"✓ Parsed DOCX: {file_path} ({len(text)} characters)")
            return text

        except ImportError:
            print("❌ python-docx not installed. Install with: pip install python-docx")
            raise
        except Exception as e:
            print(f"❌ Failed to parse DOCX: {str(e)}")
            raise

    @staticmethod
    def parse_markdown(file_path: str) -> str:
        """
        Parse Markdown file

        Args:
            file_path: Path to Markdown file

        Returns:
            Extracted text
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            print(f"✓ Parsed Markdown: {file_path} ({len(text)} characters)")
            return text

        except Exception as e:
            print(f"❌ Failed to parse Markdown: {str(e)}")
            raise

    @staticmethod
    def parse_text(file_path: str) -> str:
        """
        Parse plain text file

        Args:
            file_path: Path to text file

        Returns:
            Extracted text
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            print(f"✓ Parsed Text: {file_path} ({len(text)} characters)")
            return text

        except Exception as e:
            print(f"❌ Failed to parse text file: {str(e)}")
            raise

    @staticmethod
    def parse_file(file_path: str) -> str:
        """
        Auto-detect file type and parse

        Args:
            file_path: Path to file

        Returns:
            Extracted text
        """
        file_ext = Path(file_path).suffix.lower()

        if file_ext == '.pdf':
            return DocumentParser.parse_pdf(file_path)
        elif file_ext == '.docx':
            return DocumentParser.parse_docx(file_path)
        elif file_ext in ['.md', '.markdown']:
            return DocumentParser.parse_markdown(file_path)
        elif file_ext == '.txt':
            return DocumentParser.parse_text(file_path)
        else:
            # Default to plain text
            return DocumentParser.parse_text(file_path)


class MetadataExtractor:
    """Extract and assign metadata to documents"""

    @staticmethod
    def extract_metadata(
        file_path: str,
        department: str,
        category: str = "general",
        version: int = 1
    ) -> Dict[str, Any]:
        """
        Extract metadata from document

        Args:
            file_path: Path to document
            department: Department that owns this document
            category: Document category
            version: Document version

        Returns:
            Metadata dictionary
        """
        file_name = Path(file_path).name
        file_size = os.path.getsize(file_path)

        metadata = {
            'document_name': file_name,
            'department': department.lower(),
            'category': category.lower(),
            'version': version,
            'date': datetime.now().isoformat(),
            'file_size': file_size,
            'file_type': Path(file_path).suffix.lower(),
            'access_level': 'internal'  # Default to internal
        }

        # Validate department
        valid_departments = ['engineering', 'hr', 'operations', 'product']
        if metadata['department'] not in valid_departments:
            raise ValueError(f"Invalid department: {department}. Must be one of {valid_departments}")

        return metadata


class DocumentIngestionPipeline:
    """End-to-end document ingestion pipeline"""

    def __init__(self, chunking_strategy: str = "semantic"):
        """
        Initialize ingestion pipeline

        Args:
            chunking_strategy: 'semantic', 'fixed', or 'hybrid'
        """
        self.parser = DocumentParser()
        self.metadata_extractor = MetadataExtractor()

        # Initialize chunking strategy
        if chunking_strategy == "fixed":
            self.chunker = FixedSizeChunking(chunk_size=500, overlap=100)
        elif chunking_strategy == "semantic":
            self.chunker = SemanticChunking(target_chunk_size=500)
        else:
            self.chunker = HybridChunking(target_size=500, overlap=100)

        self.chunking_strategy = chunking_strategy
        print(f"✓ Initialized ingestion pipeline with {chunking_strategy} chunking")

    async def ingest_document(
        self,
        file_path: str,
        department: str,
        category: str = "general",
        version: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Ingest single document and return chunks

        Args:
            file_path: Path to document
            department: Department that owns document
            category: Document category
            version: Document version

        Returns:
            List of chunk dictionaries with text, metadata, and index
        """
        try:
            # Parse document
            text = self.parser.parse_file(file_path)

            # Extract metadata
            metadata = self.metadata_extractor.extract_metadata(
                file_path, department, category, version
            )

            # Chunk document
            chunks = self.chunker.chunk(text, metadata)

            # Transform to output format
            chunk_list = []
            for chunk in chunks:
                chunk_dict = {
                    'text': chunk.text,
                    'metadata': chunk.metadata,
                    'chunk_index': chunk.chunk_index
                }
                chunk_list.append(chunk_dict)

            print(f"✓ Ingested document: {metadata['document_name']} → {len(chunk_list)} chunks")
            return chunk_list

        except Exception as e:
            print(f"❌ Ingestion failed: {str(e)}")
            raise

    async def ingest_batch(
        self,
        file_paths: List[str],
        department: str,
        category: str = "general"
    ) -> List[Dict[str, Any]]:
        """
        Ingest multiple documents

        Args:
            file_paths: List of file paths
            department: Department
            category: Document category

        Returns:
            List of all chunks from all documents
        """
        all_chunks = []

        for i, file_path in enumerate(file_paths, 1):
            print(f"\n[{i}/{len(file_paths)}] Ingesting: {file_path}")
            chunks = await self.ingest_document(
                file_path, department, category, version=1
            )
            all_chunks.extend(chunks)

        print(f"\n✓ Batch ingestion complete: {len(all_chunks)} total chunks from {len(file_paths)} documents")
        return all_chunks


# Example usage and testing
if __name__ == "__main__":
    import asyncio

    async def test_ingestion():
        """Test ingestion pipeline"""

        # Create test document
        test_file = "/tmp/test_document.txt"
        with open(test_file, 'w') as f:
            f.write("""
            Enterprise Knowledge Base Test Document

            This is a sample document for the Enterprise Knowledge Assistant.
            It contains information about company policies and procedures.

            Leave Policy:
            All employees are entitled to 20 days of paid leave per year.
            Additional 5 days can be taken as unpaid leave.

            Deployment Process:
            1. Create feature branch from main
            2. Implement changes
            3. Submit pull request
            4. Wait for code review and CI/CD
            5. Merge to main and deploy to production

            Incident Escalation:
            Level 1: Initial response by support team
            Level 2: Engineering team involvement
            Level 3: Management review
            Level 4: Executive escalation
            """)

        # Initialize pipeline
        pipeline = DocumentIngestionPipeline(chunking_strategy="semantic")

        # Ingest document
        chunks = await pipeline.ingest_document(
            test_file,
            department="Engineering",
            category="policies"
        )

        print(f"\n📊 Ingestion Results:")
        print(f"   Total chunks: {len(chunks)}")
        for i, chunk in enumerate(chunks[:3], 1):
            print(f"\n   Chunk {i}:")
            print(f"   Text: {chunk['text'][:100]}...")
            print(f"   Metadata: {chunk['metadata']}")

    # Run test
    asyncio.run(test_ingestion())
