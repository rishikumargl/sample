# RAG System Testing Guide

## Quick Start

### 1. Setup Environment

```bash
# Install backend dependencies
cd backend
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="sk-your-api-key-here"
export CORS_ORIGINS="http://localhost:3000"
export DEBUG="true"
```

### 2. Start Backend RAG Server

```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
✓ RAG components initialized
Uvicorn running on http://0.0.0.0:8000
```

### 3. Start Frontend

In a new terminal:
```bash
cd frontend
npm run dev
```

Frontend runs at `http://localhost:3000`

---

## Testing Endpoints

### Test 1: Health Check

```bash
curl http://localhost:8000/health
```

Expected Response:
```json
{
  "status": "healthy",
  "message": "Enterprise Knowledge Assistant API is running",
  "vector_store": {
    "collection_name": "enterprise_knowledge",
    "document_count": 0,
    "embedding_dimension": 1536
  },
  "rag_enabled": true
}
```

### Test 2: RAG Configuration

```bash
curl http://localhost:8000/api/rag/config
```

Expected Response:
```json
{
  "embedding_model": "text-embedding-3-small",
  "embedding_dimension": 1536,
  "generation_model": "gpt-3.5-turbo",
  "vector_store": "chromadb",
  "chunking_strategies": ["semantic", "fixed", "hybrid"],
  "search_types": ["vector", "keyword", "hybrid"]
}
```

### Test 3: Upload Test Document

```bash
# Create a sample document
cat > /tmp/leave_policy.txt << 'EOF'
EMPLOYEE LEAVE POLICY

All full-time employees are entitled to 20 working days of paid annual leave per calendar year.

Additional entitlements:
- Senior employees (5+ years): +5 additional days
- Managers (3+ years): +3 additional days

LEAVE REQUEST PROCEDURE:
1. Submit leave request at least 2 weeks in advance
2. Use the HR portal or email your manager
3. Approval is granted based on team requirements

SICK LEAVE:
- 10 working days per year for medical reasons
- Medical certificate required for absences exceeding 3 consecutive days
EOF

# Upload to knowledge base
curl -X POST http://localhost:8000/api/documents/upload \
  -F "file=@/tmp/leave_policy.txt" \
  -F "department=hr" \
  -F "category=policies"
```

Expected Response:
```json
{
  "status": "success",
  "document": "leave_policy.txt",
  "department": "hr",
  "chunks_created": 5,
  "chunks_indexed": 5,
  "message": "Successfully ingested leave_policy.txt with 5 chunks"
}
```

### Test 4: Chat Query (Main RAG Test)

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the leave policy?",
    "department": "hr",
    "category": "policies",
    "chunking_strategy": "semantic",
    "search_type": "hybrid",
    "top_k": 5
  }'
```

Expected Response:
```json
{
  "query": "What is the leave policy?",
  "answer": "All full-time employees are entitled to 20 working days of paid annual leave per calendar year. Additionally, senior employees with 5 or more years of service receive 5 extra days, and managers with 3 years of experience get 3 additional days.",
  "sources": [
    {
      "document_name": "leave_policy.txt",
      "chunk_index": 0,
      "snippet": "All full-time employees are entitled to 20 working days of paid annual leave...",
      "department": "hr"
    }
  ],
  "confidence": 0.92,
  "hallucination_risk": false,
  "is_fallback": false,
  "retrieval_time_ms": 145,
  "generation_time_ms": 1520,
  "total_time_ms": 1665,
  "chunks_retrieved": 3,
  "department": "hr"
}
```

### Test 5: Department Access Control

**Test 1: HR User Can See HR Documents**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the leave policy?",
    "department": "hr"
  }'
```
✅ Returns answer from leave_policy.txt

**Test 2: Engineering User Cannot See HR Documents**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the leave policy?",
    "department": "engineering"
  }'
```
✅ Returns: "I cannot find a reliable answer to this question in the knowledge base."

**Test 3: Missing Department (Fails)**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the leave policy?"
  }'
```
❌ Returns 400 error: "Invalid department"

---

## Testing Different Chunking Strategies

### Test with Fixed-Size Chunking

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the leave policy?",
    "department": "hr",
    "chunking_strategy": "fixed"
  }'
```

### Test with Semantic Chunking

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the leave policy?",
    "department": "hr",
    "chunking_strategy": "semantic"
  }'
```

### Compare Results
- Note: response times and number of chunks retrieved may differ
- Semantic typically: fewer, larger, more coherent chunks
- Fixed-size typically: more, consistent-sized chunks

---

## Testing Retrieval Methods

### Test Vector Search Only

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the leave policy?",
    "department": "hr",
    "search_type": "vector"
  }'
```

### Test Keyword Search Only

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the leave policy?",
    "department": "hr",
    "search_type": "keyword"
  }'
```

### Test Hybrid Search (Recommended)

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the leave policy?",
    "department": "hr",
    "search_type": "hybrid"
  }'
```

Expected: Hybrid usually has best accuracy (90-95%)

---

## Testing Hallucination Control

### Test 1: Query with Sufficient Context

```bash
# Upload another document first
cat > /tmp/deployment.txt << 'EOF'
DEPLOYMENT PROCESS

1. Create feature branch from main
2. Implement changes with unit tests
3. Submit pull request for code review
4. Address review feedback
5. Wait for CI/CD pipeline to pass
6. Merge to main branch
7. Deploy to staging environment
8. Run integration tests in staging
9. Deploy to production

ROLLBACK PROCEDURES:
If issues occur after deployment:
- Notify incident commander
- Gather telemetry and logs
- Revert to previous stable commit
- Deploy rolled-back code
EOF

curl -X POST http://localhost:8000/api/documents/upload \
  -F "file=@/tmp/deployment.txt" \
  -F "department=engineering" \
  -F "category=procedures"

# Now ask a question that has answer in documents
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the deployment process?",
    "department": "engineering"
  }'
```

Expected:
- `confidence`: 0.8-0.95 (high)
- `hallucination_risk`: false
- `sources`: Contains deployment.txt chunks

### Test 2: Query without Sufficient Context

```bash
# Ask question about something NOT in documents
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do I configure Kubernetes?",
    "department": "engineering"
  }'
```

Expected:
- `answer`: "I cannot find a reliable answer to this question in the knowledge base."
- `confidence`: 0.0-0.4 (low)
- `hallucination_risk`: true
- `is_fallback`: true
- `sources`: Empty array

This prevents the system from fabricating information!

---

## Testing Query Caching

### Test Cache Hit Performance

```bash
# First query - hits vector store
time curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the leave policy?",
    "department": "hr"
  }'

# Second identical query - hits cache (10-20ms faster)
time curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the leave policy?",
    "department": "hr"
  }'
```

Second query should be 10-20x faster!

---

## Testing with Multiple Documents

### Create Multi-Department Knowledge Base

```bash
# HR Document
cat > /tmp/hr_benefits.txt << 'EOF'
EMPLOYEE BENEFITS

Health Insurance:
- Comprehensive medical coverage
- Dental and vision included
- Family plan available

401k Retirement:
- Company matches up to 5%
- Vesting period: 4 years
EOF

# Engineering Document
cat > /tmp/eng_tools.txt << 'EOF'
ENGINEERING TOOLS

Development Environment:
- IDE: VS Code or IntelliJ
- Version Control: Git
- Testing: Jest and Pytest

CI/CD Pipeline:
- GitHub Actions for automation
- Automated testing on all PRs
- Auto-deployment to staging
EOF

# Operations Document
cat > /tmp/ops_monitoring.txt << 'EOF'
MONITORING AND ALERTS

System Metrics:
- CPU usage (target < 80%)
- Memory usage (target < 85%)
- Disk space (alert at 85%)
- Network latency (target < 100ms)

Alert Thresholds:
- Critical: CPU > 95% for 5 min
- Warning: Memory > 80% for 10 min
EOF

# Upload all
for file in /tmp/hr_benefits.txt /tmp/eng_tools.txt /tmp/ops_monitoring.txt; do
  dept=$(basename "$file" .txt | cut -d'_' -f1)
  curl -X POST http://localhost:8000/api/documents/upload \
    -F "file=@$file" \
    -F "department=$dept"
done
```

### Test Cross-Department Isolation

```bash
# HR asking about benefits - should work
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What health insurance do we have?",
    "department": "hr"
  }'
# ✅ Returns benefits information

# Engineering asking about benefits - should NOT work
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What health insurance do we have?",
    "department": "engineering"
  }'
# ✅ Returns: "I cannot find a reliable answer"

# Engineering asking about tools - should work
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What tools should I use for development?",
    "department": "engineering"
  }'
# ✅ Returns tools information
```

---

## Checking System Statistics

```bash
curl http://localhost:8000/api/stats
```

Example Response:
```json
{
  "vector_store": {
    "collection_name": "enterprise_knowledge",
    "document_count": 45,
    "embedding_dimension": 1536
  },
  "system": "operational"
}
```

---

## Frontend Testing

### Manual Testing via UI

1. Open http://localhost:3000
2. Select department from dropdown
3. Enter question in chat input
4. Observe:
   - Answer displayed in chat
   - Sources shown below answer
   - Confidence indicator
   - Loading spinner during processing

### Expected Behavior

- ✅ Chat input disabled during response
- ✅ Sources appear with document names
- ✅ Department filter works correctly
- ✅ Fallback messages display for unknown questions
- ✅ Response time reasonable (< 3 seconds)

---

## Debugging

### Enable Debug Logging

```bash
export DEBUG="true"
python -m uvicorn app.main:app --reload
```

### Check Vector Store Contents

```bash
# In Python REPL
from backend.rag.vector_store import ChromaVectorStore
import asyncio

async def debug():
    store = ChromaVectorStore()
    stats = await store.get_stats()
    print(stats)

asyncio.run(debug())
```

### Profile Response Times

Add timing to your test:
```bash
# Using Python requests library
import requests
import time

start = time.time()
response = requests.post(
    'http://localhost:8000/api/chat',
    json={'query': 'What is the leave policy?', 'department': 'hr'}
)
elapsed = time.time() - start

print(f"Total time: {elapsed*1000:.0f}ms")
print(f"Retrieval: {response.json()['retrieval_time_ms']}ms")
print(f"Generation: {response.json()['generation_time_ms']}ms")
```

---

## Troubleshooting

### Issue: "I cannot find a reliable answer" for all queries

**Solution:**
1. Check documents uploaded: `curl http://localhost:8000/api/stats`
2. Verify department matches: documents are in 'hr', query uses 'hr'
3. Check document content: text should clearly contain answer terms
4. Verify embedding model: OPENAI_API_KEY is set and valid

### Issue: Slow response times (> 5 seconds)

**Solution:**
1. Check OpenAI API rate limits
2. Use hybrid search instead of keyword-only
3. Reduce top_k parameter
4. Check if using cached responses

### Issue: Different responses for same query

**Solution:**
1. Cache might be cleared (temporary files deleted)
2. Different chunking strategy selected
3. Different search_type used
4. LLM temperature variation (even at 0.2)

### Issue: Department filter not working

**Solution:**
1. Verify department spelling (lowercase in API)
2. Check document was uploaded with correct department
3. Test with known working department
4. Review error logs for more details

---

## Performance Benchmarking

### Run Benchmark

```python
# benchmark.py
import asyncio
import time
import requests

async def benchmark():
    queries = [
        ("What is the leave policy?", "hr"),
        ("How do I deploy?", "engineering"),
        ("What are monitoring thresholds?", "operations"),
    ]
    
    results = []
    for query, dept in queries:
        start = time.time()
        response = requests.post(
            'http://localhost:8000/api/chat',
            json={'query': query, 'department': dept}
        )
        elapsed = time.time() - start
        
        results.append({
            'query': query,
            'department': dept,
            'total_time_ms': elapsed * 1000,
            'retrieval_time_ms': response.json()['retrieval_time_ms'],
            'generation_time_ms': response.json()['generation_time_ms'],
            'confidence': response.json()['confidence']
        })
    
    # Print results
    for r in results:
        print(f"{r['query']}: {r['total_time_ms']:.0f}ms (retrieval: {r['retrieval_time_ms']}ms, gen: {r['generation_time_ms']}ms)")

asyncio.run(benchmark())
```

---

## Success Criteria

- ✅ Health check returns 200 OK
- ✅ Documents upload successfully
- ✅ Chat queries return answers with sources
- ✅ Department filtering works correctly
- ✅ Hallucination control prevents false answers
- ✅ Confidence scores reflect answer quality
- ✅ Cache improves response times
- ✅ Typical latency < 3 seconds (excluding LLM)

---

**All tests passing?** 🎉 Your RAG system is ready for production!
