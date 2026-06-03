from fastapi import APIRouter, HTTPException
from backend.app.models import ChatRequest, ChatResponse

router = APIRouter(tags=["chat"], prefix="/api")

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    return ChatResponse(
        answer="This is a placeholder response. RAG implementation coming soon.",
        sources=[],
        confidence=0.0,
        is_hallucination_risk=True,
        warning_message="RAG system not yet implemented. This is a mock response."
    )

@router.get("/chat/history/{user_id}")
async def get_chat_history(user_id: str):
    return {"message": "Chat history feature coming soon"}
