"""Generator - Local HF LLM with hallucination control"""

import os
import time
from typing import List, Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

try:
    from transformers import pipeline
except ImportError:
    raise ValueError("transformers not installed. Run: pip install transformers torch")

# Load .env
load_dotenv(Path.cwd() / ".env")

# Use local Hugging Face model for text generation
# DistilGPT2 is lightweight for local inference
LLM_MODEL = "distilgpt2"
GENERATION_DEVICE = -1  # -1 = CPU, 0+ = GPU

try:
    _generator_pipeline = pipeline(
        "text-generation",
        model=LLM_MODEL,
        device=GENERATION_DEVICE,
    )
except Exception as e:
    raise ValueError(f"Failed to load local LLM model: {str(e)}")


class AnswerGenerator:
    """Generate answers using local HF LLM"""

    def __init__(self, model: str = None):
        self.pipeline = _generator_pipeline
        self.model = model or LLM_MODEL
        self.max_tokens = 500

    async def generate_answer(
        self,
        query: str,
        retrieved_chunks: List[Dict[str, Any]],
        filters: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate answer from chunks"""
        start_time = time.time()
        try:
            context = self._prepare_context(retrieved_chunks)
            system_prompt = self._build_system_prompt(filters, context)

            # Local inference - combine system prompt + query
            full_prompt = f"{system_prompt}\n\nUser: {query}\nAssistant:"

            # Generate using local pipeline
            result = self.pipeline(
                full_prompt,
                max_length=self.max_tokens,
                temperature=0.2,
                top_p=0.9,
                do_sample=True
            )
            answer = result[0]["generated_text"].split("Assistant:")[-1].strip()
            risk = self._assess_hallucination_risk(answer, context, retrieved_chunks)

            sources = [
                {
                    "document_name": c.get("metadata", {}).get("document_name", "Unknown"),
                    "chunk_index": c.get("metadata", {}).get("chunk_index", 0),
                    "snippet": c.get("text", "")[:200],
                    "department": c.get("metadata", {}).get("department", "Unknown"),
                }
                for c in retrieved_chunks
            ]

            confidence = self._calculate_confidence(answer, len(retrieved_chunks), risk)

            return {
                "answer": answer,
                "sources": sources,
                "confidence": confidence,
                "hallucination_risk": risk,
                "generation_time_ms": int((time.time() - start_time) * 1000),
                "model": self.model,
                "is_fallback": self._is_fallback_response(answer)
            }
        except Exception as e:
            return {
                "answer": "Error processing your question.",
                "sources": [],
                "confidence": 0.0,
                "hallucination_risk": True,
                "error": str(e),
                "is_fallback": True
            }

    def _build_system_prompt(self, filters: Dict[str, Any], context: str) -> str:
        dept = filters.get("department", "Unknown")
        return f"""You are an Enterprise Assistant for {dept}.

INSTRUCTIONS:
1. Answer ONLY from provided context
2. If insufficient: say "I cannot find a reliable answer."
3. Do NOT use external knowledge
4. Cite sources

CONTEXT:
{context}"""

    @staticmethod
    def _prepare_context(chunks: List[Dict[str, Any]]) -> str:
        if not chunks:
            return "No context available."
        parts = []
        for i, c in enumerate(chunks, 1):
            doc = c.get("metadata", {}).get("document_name", "Unknown")
            idx = c.get("metadata", {}).get("chunk_index", 0)
            text = c.get("text", "")[:300]
            parts.append(f"[{i}. {doc} #{idx}]\n{text}")
        return "\n".join(parts)

    @staticmethod
    def _assess_hallucination_risk(answer: str, context: str, chunks: List[Dict[str, Any]]) -> bool:
        fallback = ["i cannot find", "not found", "insufficient"]
        if any(p in answer.lower() for p in fallback):
            return False
        answer_words = set(answer.lower().split())
        context_words = set(context.lower().split())
        overlap = len(answer_words & context_words) / len(answer_words) if answer_words else 0
        return overlap < 0.3

    @staticmethod
    def _calculate_confidence(answer: str, chunk_count: int, risk: bool) -> float:
        base = min(chunk_count / 5, 1.0) * 0.7
        return min(max(base + (0.0 if risk else 0.3), 0.0), 1.0)

    @staticmethod
    def _is_fallback_response(answer: str) -> bool:
        return "i cannot find" in answer.lower()


class RAGOrchestrator:
    """Orchestrate RAG pipeline"""

    def __init__(self, embedding_generator, retrieval_system, answer_generator: AnswerGenerator, enable_cache: bool = True):
        self.embedding_generator = embedding_generator
        self.retrieval_system = retrieval_system
        self.answer_generator = answer_generator
        self.cache = {} if enable_cache else None

    async def process_query(self, query: str, filters: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process RAG query"""
        start_time = time.time()
        options = options or {}
        cache_key = f"{query}:{filters.get('department')}".lower()

        if self.cache and cache_key in self.cache:
            return self.cache[cache_key]

        try:
            query_embedding = await self.embedding_generator.generate_embedding(query)
            retrieval_result = await self.retrieval_system.search(
                query=query,
                query_embedding=query_embedding,
                filters=filters,
                search_type=options.get("search", "hybrid"),
                top_k=options.get("top_k", 5)
            )
            chunks = retrieval_result.get("chunks", [])
            answer_result = await self.answer_generator.generate_answer(query, chunks, filters)

            response = {
                "query": query,
                "answer": answer_result["answer"],
                "sources": answer_result["sources"],
                "confidence": answer_result["confidence"],
                "hallucination_risk": answer_result["hallucination_risk"],
                "is_fallback": answer_result.get("is_fallback", False),
                "total_time_ms": int((time.time() - start_time) * 1000),
                "chunks_retrieved": len(chunks),
                "department": filters.get("department"),
            }

            if self.cache:
                self.cache[cache_key] = response
            return response

        except Exception as e:
            return {
                "query": query,
                "answer": "Error processing question.",
                "sources": [],
                "confidence": 0.0,
                "hallucination_risk": True,
                "error": str(e),
                "is_fallback": True
            }
