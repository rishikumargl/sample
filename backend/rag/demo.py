"""
RAG System Demonstration - Shows complete RAG flow with test data
Use this to test the RAG system without running the full backend
"""

import asyncio
import os
from pathlib import Path

from .embeddings import EmbeddingGenerator
from .chunking_strategies import FixedSizeChunking, SemanticChunking
from .vector_store import ChromaVectorStore
from .retrieval import VectorRetrieval, KeywordRetrieval, HybridRetrieval
from .generator import AnswerGenerator, RAGOrchestrator
from .ingestion import DocumentIngestionPipeline


# Sample documents for testing
SAMPLE_DOCUMENTS = {
    "leave_policy.txt": {
        "content": """
        EMPLOYEE LEAVE POLICY - HUMAN RESOURCES

        1. ANNUAL LEAVE ENTITLEMENT
        All full-time employees are entitled to 20 working days of paid annual leave per calendar year.
        Additional entitlements:
        - Senior employees (5+ years): +5 additional days
        - Managers (3+ years): +3 additional days

        2. LEAVE REQUEST PROCEDURE
        - Submit leave request at least 2 weeks in advance
        - Use the HR portal or email your manager
        - Approval is granted based on team requirements
        - Peak periods may have restricted leave availability

        3. SICK LEAVE
        - 10 working days per year for medical reasons
        - Medical certificate required for absences exceeding 3 consecutive days
        - Does not carry over to next year

        4. MATERNITY/PATERNITY LEAVE
        - Maternity: 4 months paid, 2 months unpaid
        - Paternity: 2 weeks paid, 2 weeks unpaid
        - Must be taken within 2 years of child's birth

        5. SPECIAL LEAVES
        - Bereavement: 3-5 days
        - Marriage: 3-5 days
        - Blood donation: 1 day per donation (max 2 per year)
        """,
        "department": "hr",
        "category": "policies"
    },

    "deployment_guide.txt": {
        "content": """
        DEPLOYMENT AND ROLLBACK PROCEDURES - ENGINEERING

        1. DEPLOYMENT PROCESS
        Step 1: Create feature branch from main
        Step 2: Implement changes with unit tests
        Step 3: Submit pull request for code review
        Step 4: Address review feedback
        Step 5: Wait for CI/CD pipeline to pass
        Step 6: Merge to main branch
        Step 7: Deploy to staging environment
        Step 8: Run integration tests in staging
        Step 9: Deploy to production during maintenance window
        Step 10: Monitor logs and metrics for 30 minutes

        2. ROLLBACK PROCEDURES
        In case of critical issues after deployment:
        - Notify the incident commander
        - Gather telemetry and logs
        - Review failure root cause
        - Execute automated rollback if available
        - Manual rollback: Revert to previous stable commit
        - Deploy rolled-back code following normal deployment process
        - Post-mortem meeting within 24 hours

        3. DEPLOYMENT WINDOWS
        - Standard deployments: Monday-Friday 02:00-06:00 UTC
        - Hotfixes: Can be deployed anytime with approval
        - Large deployments: Friday before 18:00 to avoid weekend emergencies

        4. MONITORING AFTER DEPLOYMENT
        - CPU usage should stay below 80%
        - Memory usage should stay below 85%
        - Error rate should remain below baseline + 5%
        - P99 latency should not increase more than 10%
        """,
        "department": "engineering",
        "category": "procedures"
    },

    "incident_escalation.txt": {
        "content": """
        INCIDENT ESCALATION PROCEDURES - OPERATIONS

        1. INCIDENT SEVERITY LEVELS
        - SEV1 (Critical): Service down, data loss, security breach - Response: Immediate
        - SEV2 (High): Major feature unavailable, significant performance impact - Response: <15 minutes
        - SEV3 (Medium): Minor features affected, workaround available - Response: <1 hour
        - SEV4 (Low): Cosmetic issues, no user impact - Response: <24 hours

        2. ESCALATION PATH
        Level 1: On-call support engineer
        - Initial triage and response
        - Attempt basic troubleshooting
        - If cannot resolve in 15 minutes, escalate to Level 2

        Level 2: Engineering team lead
        - Deep technical investigation
        - May involve multiple engineers
        - If cannot resolve in 45 minutes, escalate to Level 3

        Level 3: Engineering manager + Team leads
        - Cross-team coordination
        - Resource allocation decisions
        - If cannot resolve in 2 hours, escalate to Level 4

        Level 4: Director + VP Engineering
        - Executive decision making
        - Customer communication
        - Post-incident review planning

        3. COMMUNICATION PROTOCOL
        - Update status page every 10 minutes
        - Notify affected customers within 5 minutes
        - Provide hourly updates for incidents lasting > 1 hour
        - Final root cause analysis within 24 hours

        4. POST-INCIDENT ACTIONS
        - Incident report filed within 24 hours
        - Root cause analysis completed within 48 hours
        - Corrective actions assigned and tracked
        - Follow-up review scheduled for 1 week later
        """,
        "department": "operations",
        "category": "incident_management"
    },

    "product_roadmap.txt": {
        "content": """
        PRODUCT ROADMAP AND FEATURE RELEASES - PRODUCT SUPPORT

        1. Q1 2024 RELEASES
        - User dashboard redesign (January)
        - Mobile app v2.0 launch (February)
        - Real-time notification system (March)

        2. Q2 2024 RELEASES
        - API v3 deprecation warning begins (April)
        - Advanced search filters (May)
        - Integration marketplace launch (June)

        3. FEATURE REQUEST PROCESS
        Customer can submit feature requests through:
        - Product portal at https://product.example.com/feedback
        - Support email: product@example.com
        - In-app feedback widget

        4. FEATURE PRIORITIZATION
        Criteria:
        - User impact (50%)
        - Technical feasibility (30%)
        - Business value (20%)

        5. KNOWN ISSUES
        - Dashboard slow with >100k items (Fix in Feb 2024)
        - Mobile app crashes on iOS 14.2 (Fixed in hotfix)
        - Email notifications delay up to 5 minutes (Investigating)
        """,
        "department": "product",
        "category": "roadmap"
    }
}


async def create_test_documents():
    """Create sample test documents"""
    test_dir = Path("/tmp/rag_demo_docs")
    test_dir.mkdir(exist_ok=True)

    for filename, doc_info in SAMPLE_DOCUMENTS.items():
        file_path = test_dir / filename
        with open(file_path, 'w') as f:
            f.write(doc_info['content'])

    return list(test_dir.glob("*.txt"))


async def demonstrate_chunking():
    """Demonstrate different chunking strategies"""
    print("\n" + "=" * 80)
    print("CHUNKING STRATEGY COMPARISON")
    print("=" * 80)

    sample_text = SAMPLE_DOCUMENTS["leave_policy.txt"]["content"]

    # Fixed-size chunking
    fixed_chunker = FixedSizeChunking(chunk_size=500, overlap=100)
    fixed_chunks = fixed_chunker.chunk(sample_text, {"department": "hr"})
    print(f"\n✓ Fixed-Size Chunking: {len(fixed_chunks)} chunks")
    print(f"  Sample chunk size: {len(fixed_chunks[0].text)} characters")

    # Semantic chunking
    semantic_chunker = SemanticChunking(target_chunk_size=500)
    semantic_chunks = semantic_chunker.chunk(sample_text, {"department": "hr"})
    print(f"\n✓ Semantic Chunking: {len(semantic_chunks)} chunks")
    if semantic_chunks:
        print(f"  Sample chunk size: {len(semantic_chunks[0].text)} characters")


async def demonstrate_rag_pipeline():
    """Demonstrate complete RAG pipeline"""
    print("\n" + "=" * 80)
    print("RAG PIPELINE DEMONSTRATION")
    print("=" * 80)

    # Initialize components
    print("\n[1/5] Initializing RAG components...")
    vector_store = ChromaVectorStore(persist_dir=None)  # In-memory
    embedding_generator = EmbeddingGenerator()
    vector_retrieval = VectorRetrieval(vector_store)
    answer_generator = AnswerGenerator()
    rag_orchestrator = RAGOrchestrator(
        embedding_generator=embedding_generator,
        retrieval_system=vector_retrieval,
        answer_generator=answer_generator,
        enable_cache=True
    )
    print("✓ RAG components ready")

    # Create test documents
    print("\n[2/5] Creating test documents...")
    doc_paths = await create_test_documents()
    print(f"✓ Created {len(doc_paths)} test documents")

    # Ingest documents
    print("\n[3/5] Ingesting documents into RAG...")
    ingestion_pipeline = DocumentIngestionPipeline(chunking_strategy="semantic")

    all_chunks = []
    for doc_path in doc_paths:
        # Get department from sample data
        filename = doc_path.name
        dept = SAMPLE_DOCUMENTS[filename]["department"]
        category = SAMPLE_DOCUMENTS[filename]["category"]

        chunks = await ingestion_pipeline.ingest_document(
            str(doc_path),
            department=dept,
            category=category
        )
        all_chunks.extend(chunks)

    print(f"✓ Ingested {len(all_chunks)} total chunks")

    # Generate embeddings and add to vector store
    print("\n[4/5] Generating embeddings and indexing...")
    chunk_texts = [chunk['text'] for chunk in all_chunks]

    # For demo, use dummy embeddings (OpenAI API requires valid key)
    embeddings = [[0.1] * 1536 for _ in chunk_texts]  # Placeholder
    print("⚠ Using placeholder embeddings (set OPENAI_API_KEY for real embeddings)")

    await vector_store.add_documents(all_chunks, embeddings)
    print(f"✓ Indexed {len(all_chunks)} chunks in vector store")

    # Test queries
    print("\n[5/5] Processing test queries...")

    test_queries = [
        {
            "query": "What is the leave policy?",
            "department": "hr",
            "department_name": "Human Resources"
        },
        {
            "query": "How do I deploy code?",
            "department": "engineering",
            "department_name": "Engineering"
        },
        {
            "query": "What is the incident escalation process?",
            "department": "operations",
            "department_name": "Operations"
        },
        {
            "query": "What new features are coming?",
            "department": "product",
            "department_name": "Product"
        }
    ]

    for i, test_query in enumerate(test_queries, 1):
        print(f"\n{'─' * 80}")
        print(f"Query {i}: {test_query['query']}")
        print(f"Department: {test_query['department_name']}")
        print(f"{'─' * 80}")

        try:
            result = await rag_orchestrator.process_query(
                query=test_query['query'],
                filters={"department": test_query['department']},
                options={"search": "hybrid", "top_k": 3}
            )

            print(f"\n📝 Answer:")
            print(f"  {result['answer'][:300]}...")

            print(f"\n📚 Sources ({len(result['sources'])}):")
            for source in result['sources'][:2]:
                print(f"  - {source['document_name']} ({source['department']})")
                print(f"    Snippet: {source['snippet'][:100]}...")

            print(f"\n📊 Metrics:")
            print(f"  Confidence: {result['confidence']:.2%}")
            print(f"  Hallucination Risk: {result['hallucination_risk']}")
            print(f"  Retrieval Time: {result['retrieval_time_ms']}ms")
            print(f"  Generation Time: {result['generation_time_ms']}ms")
            print(f"  Total Time: {result['total_time_ms']}ms")

        except Exception as e:
            print(f"❌ Error: {str(e)}")


async def demonstrate_access_control():
    """Demonstrate Use Case 3 requirement: Department access control"""
    print("\n" + "=" * 80)
    print("USE CASE 3: DEPARTMENT-LEVEL ACCESS CONTROL")
    print("=" * 80)

    print("""
    ✓ Strict department-level filtering ensures:

    1. ISOLATION: HR department cannot see Engineering documents
    2. GOVERNANCE: Each department has its own knowledge scope
    3. SECURITY: Sensitive information stays within department
    4. COMPLIANCE: Access boundaries enforced at database level

    Example scenario:
    - User in HR asks "What is the leave policy?" → Gets HR documents only
    - User in Engineering asks same question → No results (info not in their scope)
    - User in Operations asks "How do I deploy?" → No results (not their responsibility)

    This ensures enterprise data governance is maintained throughout the RAG system.
    """)


async def main():
    """Run all demonstrations"""
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + " ENTERPRISE KNOWLEDGE ASSISTANT - RAG SYSTEM DEMONSTRATION".center(78) + " ║")
    print("║" + " Use Case 3: Multi-Department Knowledge Base with Access Control".center(78) + " ║")
    print("║" + " " * 78 + "║")
    print("╚" + "═" * 78 + "╝")

    # Run demonstrations
    await demonstrate_chunking()
    await demonstrate_access_control()

    # Note: Full pipeline demo requires valid OpenAI API key
    print("""
    ⚠️  NOTE: Complete RAG pipeline demonstration requires OpenAI API key
    Set OPENAI_API_KEY environment variable to run the full pipeline demo

    To run backend with RAG:
    1. Set OPENAI_API_KEY and CORS_ORIGINS environment variables
    2. Run: python backend/app/main.py
    3. Test with: curl http://localhost:8000/api/chat -H "Content-Type: application/json" \\
                   -d '{"query":"What is the leave policy?","department":"hr"}'
    """)


if __name__ == "__main__":
    asyncio.run(main())
