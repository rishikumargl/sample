from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

class Department(str, Enum):
    engineering = "engineering"
    hr = "hr"
    operations = "operations"
    product = "product"

class DocumentCategory(str, Enum):
    policy = "policy"
    technical = "technical"
    incident = "incident"
    procedure = "procedure"
    faq = "faq"
    release_notes = "release_notes"

class ChatRequest(BaseModel):
    question: str
    user_id: str = "demo"
    department: Optional[Department] = None
    top_k: int = 5

class SourceReference(BaseModel):
    document_id: int
    document_name: str
    relevance_score: float
    excerpt: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceReference] = []
    confidence: float = 0.0
    is_hallucination_risk: bool = False
    warning_message: Optional[str] = None

class Document(BaseModel):
    id: int
    name: str
    department: Department
    category: DocumentCategory
    chunks_count: int

class HealthResponse(BaseModel):
    status: str
    message: str
    version: str = "1.0.0"
