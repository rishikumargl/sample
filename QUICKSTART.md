# Quick Start - Enterprise Knowledge Assistant

## Start in 5 Minutes

### 1. Install Dependencies
```bash
cd backend && pip install -r requirements.txt
cd ../frontend && npm install
```

### 2. Set Environment
```bash
export OPENAI_API_KEY="sk-your-key-here"
export CORS_ORIGINS="http://localhost:3000"
```

### 3. Start Backend
```bash
cd backend
python -m uvicorn app.main:app --reload
```

### 4. Start Frontend
```bash
cd frontend
npm run dev
```

### 5. Open Browser
Go to **http://localhost:3000**

---

## Test RAG System

### Upload Document
```bash
curl -X POST http://localhost:8000/api/documents/upload \
  -F "file=@leave_policy.txt" \
  -F "department=hr"
```

### Ask Question
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query":"What is leave policy?","department":"hr"}'
```

---

## Key Features

✅ Document Ingestion (PDF, DOCX, TXT, Markdown)  
✅ Hybrid Search (Vector + Keyword)  
✅ Hallucination Control  
✅ Department Isolation  
✅ Source Attribution  
✅ Confidence Scoring  
✅ Query Caching  

---

See **FINAL_STATUS.md** for complete documentation.
