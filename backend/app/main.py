from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path=Path(__file__).parent.parent.parent / ".env")

# Add RAG module to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# RAG imports
from rag.embeddings import EmbeddingGenerator
from rag.chunking_strategies import FixedSizeChunking, SemanticChunking
from rag.vector_store import ChromaVectorStore
from rag.retrieval import VectorRetrieval, KeywordRetrieval, HybridRetrieval
from rag.generator import AnswerGenerator, RAGOrchestrator
from rag.ingestion import DocumentIngestionPipeline, DocumentParser, MetadataExtractor

app = FastAPI(
    title="Enterprise Knowledge Assistant API",
    description="Production-ready RAG assistant for Use Case 3",
    version="1.0.0"
)

cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# INITIALIZE RAG COMPONENTS
# ==========================================

# Initialize vector store
vector_store = ChromaVectorStore(persist_dir="./data/vector_store")

# Initialize RAG components
embedding_generator = EmbeddingGenerator()
vector_retrieval = VectorRetrieval(vector_store)
answer_generator = AnswerGenerator()  # Uses local distilgpt2 model
ingestion_pipeline = DocumentIngestionPipeline(chunking_strategy="semantic")

# Initialize RAG orchestrator
rag_orchestrator = RAGOrchestrator(
    embedding_generator=embedding_generator,
    retrieval_system=VectorRetrieval(vector_store),
    answer_generator=answer_generator,
    enable_cache=True
)

print("✓ RAG components initialized")


# ==========================================
# PYDANTIC MODELS
# ==========================================

class ChatRequest(BaseModel):
    """Chat request schema"""
    query: str
    user_id: str
    department: str
    category: str = "general"
    chunking_strategy: str = "semantic"
    search_type: str = "hybrid"
    top_k: int = 5


class DocumentUploadRequest(BaseModel):
    """Document upload metadata"""
    department: str
    category: str = "general"
    version: int = 1


class ChatResponse(BaseModel):
    """Chat response schema"""
    query: str
    answer: str
    sources: list
    confidence: float
    hallucination_risk: bool
    is_fallback: bool
    retrieval_time_ms: int
    generation_time_ms: int
    total_time_ms: int
    chunks_retrieved: int
    department: str


# ==========================================
# HEALTH & MONITORING
# ==========================================

@app.get("/test-response")
async def test_response():
    """Test endpoint to verify responses"""
    return {"status": "test response working", "timestamp": "2024-01-01"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        stats = await vector_store.get_stats()
        return {
            "status": "healthy",
            "message": "Enterprise Knowledge Assistant API is running",
            "vector_store": stats,
            "rag_enabled": True
        }
    except Exception as e:
        return {
            "status": "degraded",
            "message": f"Vector store issue: {str(e)}",
            "rag_enabled": False
        }


@app.get("/api/stats")
async def get_stats():
    """Get RAG system statistics"""
    try:
        stats = await vector_store.get_stats()
        return {
            "vector_store": stats,
            "system": "operational"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# CHAT ENDPOINT - MAIN RAG FLOW
# ==========================================

@app.post("/api/chat")
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Main chat endpoint - processes queries through RAG pipeline

    CRITICAL: Use Case 3 Implementation
    - Enforces department-level access control via filters
    - Returns answers only from department-specific documents
    - Includes hallucination control and source attribution
    """
    import sys
    print(f"🔵 Chat endpoint called with query: {request.query}", file=sys.stderr, flush=True)
    try:
        # Validate department
        valid_departments = ["engineering", "hr", "operations", "product"]
        if request.department.lower() not in valid_departments:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid department. Must be one of: {valid_departments}"
            )

        # Build filters for department-level isolation
        filters = {
            "department": request.department.lower(),
            "category": request.category.lower() if request.category else "general"
        }

        # Build options
        options = {
            "search": request.search_type,
            "chunking": request.chunking_strategy,
            "top_k": request.top_k
        }

        print(f"DEBUG: Processing query: {request.query[:50]}")
        # Process query through RAG orchestrator
        result = await rag_orchestrator.process_query(
            query=request.query,
            filters=filters,
            options=options
        )
        print(f"DEBUG: Result keys: {list(result.keys())}")
        print(f"DEBUG: Result answer: {result.get('answer', '')[:50]}")

        # Transform to ChatResponse format
        return ChatResponse(
            query=request.query,
            answer=result['answer'],
            sources=result['sources'],
            confidence=result['confidence'],
            hallucination_risk=result['hallucination_risk'],
            is_fallback=result.get('is_fallback', False),
            retrieval_time_ms=result.get('total_time_ms', 0),  # Use total_time_ms as retrieval
            generation_time_ms=result.get('total_time_ms', 0),  # Use total_time_ms as generation
            total_time_ms=result['total_time_ms'],
            chunks_retrieved=result['chunks_retrieved'],
            department=result['department']
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"❌ Chat endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# DOCUMENT MANAGEMENT
# ==========================================

@app.post("/api/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    department: str = Query(...),
    category: str = Query("general"),
    version: int = Query(1)
):
    """
    Upload and ingest document into RAG system

    Args:
        file: Document file (PDF, DOCX, TXT, Markdown)
        department: Department that owns this document
        category: Document category
        version: Document version
    """
    try:
        # Validate department
        valid_departments = ["engineering", "hr", "operations", "product"]
        if department.lower() not in valid_departments:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid department: {department}"
            )

        # Save uploaded file temporarily
        file_path = f"/tmp/{file.filename}"
        with open(file_path, 'wb') as f:
            content = await file.read()
            f.write(content)

        # Ingest document
        chunks = await ingestion_pipeline.ingest_document(
            file_path=file_path,
            department=department.lower(),
            category=category.lower(),
            version=version
        )

        # Generate embeddings for chunks
        chunk_texts = [chunk['text'] for chunk in chunks]
        embeddings = await embedding_generator.generate_embeddings_batch(chunk_texts)

        # Add to vector store
        inserted = await vector_store.add_documents(chunks, embeddings)

        # Clean up temp file
        os.remove(file_path)

        return {
            "status": "success",
            "document": file.filename,
            "department": department,
            "chunks_created": len(chunks),
            "chunks_indexed": inserted,
            "message": f"Successfully ingested {file.filename} with {len(chunks)} chunks"
        }

    except Exception as e:
        print(f"❌ Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/documents")
async def list_documents(department: str = Query(None)):
    """
    List documents by department

    Args:
        department: Filter by department (optional)

    Returns:
        List of documents with metadata
    """
    try:
        stats = await vector_store.get_stats()
        return {
            "documents": [],
            "total": stats['document_count'],
            "department_filter": department,
            "note": "Document listing endpoint - implement as needed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/documents/{document_name}")
async def delete_document(
    document_name: str,
    department: str = Query(...)
):
    """
    Delete document from knowledge base

    Args:
        document_name: Name of document to delete
        department: Department that owns the document
    """
    try:
        deleted = await vector_store.delete_by_metadata({
            "department": department.lower(),
            "document_name": document_name
        })

        return {
            "status": "success",
            "document": document_name,
            "chunks_deleted": deleted
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# USER MANAGEMENT
# ==========================================

@app.get("/api/users/{user_id}")
async def get_user(user_id: str):
    """Get user information"""
    return {
        "id": user_id,
        "name": f"User {user_id}",
        "role": "user",
        "department": "engineering",
        "created_at": "2024-01-01T00:00:00Z"
    }


@app.post("/api/users")
async def create_user(department: str, role: str = "user"):
    """Create new user with department assignment"""
    return {
        "id": "user_123",
        "name": "New User",
        "role": role,
        "department": department,
        "created_at": "2024-01-01T00:00:00Z"
    }


# ==========================================
# DIAGNOSTIC ENDPOINTS
# ==========================================

@app.get("/api/rag/config")
async def get_rag_config():
    """Get RAG system configuration"""
    return {
        "embedding_model": "text-embedding-3-small",
        "embedding_dimension": 1536,
        "generation_model": "gpt-3.5-turbo",
        "vector_store": "chromadb",
        "chunking_strategies": ["semantic", "fixed", "hybrid"],
        "search_types": ["vector", "keyword", "hybrid"]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
