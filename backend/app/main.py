from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(
    title="Enterprise Knowledge Assistant API",
    description="Production-ready RAG assistant",
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

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Enterprise Knowledge Assistant API is running"}

@app.post("/api/chat")
async def chat(question: str, user_id: str = "demo"):
    return {
        "answer": "This is a placeholder response. RAG implementation coming soon.",
        "sources": [],
        "confidence": 0.0,
        "is_hallucination_risk": True,
        "warning_message": "RAG system not yet implemented. This is a mock response."
    }

@app.get("/api/documents")
async def list_documents():
    return {"documents": [], "total": 0}

@app.post("/api/documents/upload")
async def upload_document():
    return {"status": "pending", "message": "Upload endpoint placeholder"}

@app.get("/api/users/{user_id}")
async def get_user(user_id: str):
    return {"id": user_id, "name": "Demo User", "role": "user"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
