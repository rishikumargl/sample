"""
Generator Module - LLM-based answer generation with hallucination control
Orchestrates the complete RAG pipeline
"""

import os
import time
from typing import List, Dict, Any, Optional
import openai


class AnswerGenerator:
    """Generate answers using LLM with strict hallucination control"""

    def __init__(self, model: str = "gpt-3.5-turbo"):
        """
        Initialize answer generator

        Args:
            model: OpenAI model to use (default: gpt-3.5-turbo)
        """
        openai.api_key = os.getenv("OPENAI_API_KEY", "")
        self.model = model
        self.max_tokens = 500

    async def generate_answer(
        self,
        query: str,
        retrieved_chunks: List[Dict[str, Any]],
        filters: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate answer from retrieved chunks with hallucination control

        CRITICAL: Implements strict hallucination control via system prompt
        - Only use provided context
        - If context insufficient, explicitly state "I cannot find a reliable answer"
        - No extrapolation from pre-training weights

        Args:
            query: User question
            retrieved_chunks: List of relevant document chunks
            filters: User metadata filters (department, etc.)
            user_context: Optional user context (role, permissions, etc.)

        Returns:
            Dict with answer, sources, confidence, and metadata
        """
        start_time = time.time()

        try:
            # Prepare context from chunks
            context_text = self._prepare_context(retrieved_chunks)

            # Build system prompt with strict instructions
            system_prompt = self._build_system_prompt(filters, context_text)

            # Call OpenAI API with function calling for reliability
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                temperature=0.2,  # Low temperature for factual responses
                max_tokens=self.max_tokens,
                top_p=0.9
            )

            answer_text = response['choices'][0]['message']['content']

            # Analyze for hallucination risk
            hallucination_risk = self._assess_hallucination_risk(
                answer_text,
                context_text,
                retrieved_chunks
            )

            # Extract sources
            sources = [
                {
                    'document_name': chunk.get('metadata', {}).get('document_name', 'Unknown'),
                    'chunk_index': chunk.get('metadata', {}).get('chunk_index', 0),
                    'snippet': chunk.get('text', '')[:200] + "...",
                    'department': chunk.get('metadata', {}).get('department', 'Unknown'),
                }
                for chunk in retrieved_chunks
            ]

            # Calculate confidence
            confidence = self._calculate_confidence(
                answer_text,
                len(retrieved_chunks),
                hallucination_risk
            )

            total_time_ms = (time.time() - start_time) * 1000

            # Log generation metrics
            print(f"[GENERATION] Generated answer in {total_time_ms:.0f}ms, confidence: {confidence:.2f}")

            return {
                "answer": answer_text,
                "sources": sources,
                "confidence": confidence,
                "hallucination_risk": hallucination_risk,
                "retrieval_count": len(retrieved_chunks),
                "generation_time_ms": int(total_time_ms),
                "model": self.model,
                "department": filters.get('department', 'Unknown'),
                "is_fallback": self._is_fallback_response(answer_text)
            }

        except Exception as e:
            print(f"❌ Answer generation failed: {str(e)}")
            return {
                "answer": "I apologize, but I encountered an error while processing your question. Please try again.",
                "sources": [],
                "confidence": 0.0,
                "hallucination_risk": True,
                "error": str(e),
                "is_fallback": True
            }

    def _build_system_prompt(self, filters: Dict[str, Any], context: str) -> str:
        """
        Build system prompt with strict instructions and context

        Args:
            filters: User metadata filters
            context: Prepared context from retrieved chunks

        Returns:
            System prompt for LLM
        """
        department = filters.get('department', 'Unknown')

        return f"""You are an Enterprise Knowledge Assistant for the {department} department.

CRITICAL INSTRUCTIONS:
1. Answer ONLY based on the provided context below
2. If the context does not contain sufficient information to answer the question, respond EXACTLY with: "I cannot find a reliable answer to this question in the knowledge base."
3. Do NOT extrapolate, infer, or use external knowledge
4. Always cite the source document when providing information
5. Be precise and factual
6. If the question is outside your scope, clearly state this

CONTEXT:
{context}

Remember: It is better to say "I cannot find a reliable answer" than to provide an incorrect answer."""

    @staticmethod
    def _prepare_context(chunks: List[Dict[str, Any]]) -> str:
        """
        Prepare context string from retrieved chunks

        Args:
            chunks: List of retrieved chunks

        Returns:
            Formatted context string
        """
        if not chunks:
            return "No relevant context found."

        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            text = chunk.get('text', '')
            metadata = chunk.get('metadata', {})
            doc_name = metadata.get('document_name', 'Unknown Document')
            chunk_idx = metadata.get('chunk_index', 0)

            context_parts.append(
                f"[Source {i}: {doc_name}, Chunk {chunk_idx}]\n{text}\n"
            )

        return "\n".join(context_parts)

    @staticmethod
    def _assess_hallucination_risk(
        answer: str,
        context: str,
        chunks: List[Dict[str, Any]]
    ) -> bool:
        """
        Assess risk of hallucination

        Args:
            answer: Generated answer
            context: Retrieved context
            chunks: Retrieved chunks

        Returns:
            True if hallucination risk is high, False otherwise
        """
        # Check for explicit fallback response
        fallback_phrases = [
            "i cannot find a reliable answer",
            "not found in the knowledge base",
            "insufficient information",
            "i don't have information"
        ]

        answer_lower = answer.lower()
        if any(phrase in answer_lower for phrase in fallback_phrases):
            return False  # Explicit uncertainty = lower risk

        # Check if answer is grounded in context
        answer_words = set(answer.lower().split())
        context_words = set(context.lower().split())

        # Calculate word overlap
        overlap = len(answer_words & context_words) / len(answer_words) if answer_words else 0

        # Risk is high if low overlap (potential hallucination)
        return overlap < 0.3

    @staticmethod
    def _calculate_confidence(
        answer: str,
        chunk_count: int,
        hallucination_risk: bool
    ) -> float:
        """
        Calculate confidence score

        Args:
            answer: Generated answer
            chunk_count: Number of retrieved chunks
            hallucination_risk: Whether hallucination risk is high

        Returns:
            Confidence score (0.0 to 1.0)
        """
        # Base score from chunk count
        base_score = min(chunk_count / 5, 1.0) * 0.7  # Max 0.7 from chunks

        # Add points if no hallucination risk
        hallucination_penalty = 0.3 if hallucination_risk else 0.0

        # Final score
        confidence = base_score + (0.3 * (1 - min(hallucination_penalty / 0.3, 1.0)))

        return min(max(confidence, 0.0), 1.0)

    @staticmethod
    def _is_fallback_response(answer: str) -> bool:
        """
        Check if response is a fallback (cannot find answer)

        Args:
            answer: Generated answer

        Returns:
            True if fallback response, False otherwise
        """
        fallback_phrases = [
            "i cannot find a reliable answer",
            "not found in the knowledge base",
            "insufficient information",
            "i don't have information"
        ]

        return any(phrase in answer.lower() for phrase in fallback_phrases)


class RAGOrchestrator:
    """Orchestrates the complete RAG pipeline"""

    def __init__(
        self,
        embedding_generator,
        retrieval_system,
        answer_generator: AnswerGenerator,
        enable_cache: bool = True
    ):
        """
        Initialize RAG orchestrator

        Args:
            embedding_generator: Embedding generation instance
            retrieval_system: Retrieval system instance
            answer_generator: Answer generator instance
            enable_cache: Enable query caching
        """
        self.embedding_generator = embedding_generator
        self.retrieval_system = retrieval_system
        self.answer_generator = answer_generator
        self.cache = {} if enable_cache else None

    async def process_query(
        self,
        query: str,
        filters: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process complete RAG query

        Steps:
        1. Check cache
        2. Generate query embedding
        3. Retrieve relevant chunks
        4. Generate answer
        5. Cache result

        Args:
            query: User question
            filters: Metadata filters (department, category, etc.)
            options: Search options (chunking strategy, search type, etc.)

        Returns:
            Complete RAG response with answer and metadata
        """
        start_time = time.time()
        options = options or {}

        # Check cache
        cache_key = f"{query}:{filters.get('department')}".lower()
        if self.cache and cache_key in self.cache:
            print(f"✓ Cache hit for query: {query[:50]}...")
            return self.cache[cache_key]

        try:
            # Generate embedding for query
            query_embedding = await self.embedding_generator.generate_embedding(query)

            # Retrieve relevant chunks
            retrieval_result = await self.retrieval_system.search(
                query=query,
                query_embedding=query_embedding,
                filters=filters,
                search_type=options.get('search', 'hybrid'),
                top_k=options.get('top_k', 5)
            )

            chunks = retrieval_result.get('chunks', [])

            # Generate answer
            answer_result = await self.answer_generator.generate_answer(
                query=query,
                retrieved_chunks=chunks,
                filters=filters
            )

            # Combine retrieval and generation results
            total_time_ms = (time.time() - start_time) * 1000

            response = {
                "query": query,
                "answer": answer_result['answer'],
                "sources": answer_result['sources'],
                "confidence": answer_result['confidence'],
                "hallucination_risk": answer_result['hallucination_risk'],
                "is_fallback": answer_result.get('is_fallback', False),
                "retrieval_time_ms": retrieval_result.get('retrieval_time_ms', 0),
                "generation_time_ms": answer_result.get('generation_time_ms', 0),
                "total_time_ms": int(total_time_ms),
                "chunks_retrieved": len(chunks),
                "department": filters.get('department'),
                "search_type": options.get('search', 'hybrid'),
                "chunking_strategy": options.get('chunking', 'semantic')
            }

            # Cache result
            if self.cache:
                self.cache[cache_key] = response
                print(f"✓ Cached query result (cache size: {len(self.cache)})")

            return response

        except Exception as e:
            print(f"❌ RAG query processing failed: {str(e)}")
            return {
                "query": query,
                "answer": "I apologize, but I encountered an error processing your question.",
                "sources": [],
                "confidence": 0.0,
                "hallucination_risk": True,
                "error": str(e),
                "is_fallback": True
            }
