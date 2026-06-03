from fastapi import APIRouter, HTTPException, Query
from typing import List
from backend.app.models import Document, Department, DocumentCategory

router = APIRouter(tags=["documents"], prefix="/api/documents")

@router.post("/upload")
async def upload_document():
    return {"status": "pending", "message": "Upload endpoint - RAG implementation coming soon"}

@router.get("/", response_model=List[Document])
async def list_documents(
    department: Department = Query(None),
    category: DocumentCategory = Query(None),
    skip: int = Query(0),
    limit: int = Query(10)
):
    return []

@router.get("/{document_id}", response_model=Document)
async def get_document(document_id: int):
    raise HTTPException(status_code=404, detail="Document not found")

@router.delete("/{document_id}")
async def delete_document(document_id: int):
    raise HTTPException(status_code=404, detail="Document not found")
