# Enterprise Knowledge Assistant - Setup Guide

## Prerequisites

- **Python 3.9+** - Check with `python --version`
- **Node.js 16+** - Check with `node --version`
- **OpenAI API Key** - Get from https://platform.openai.com/api/keys
- **Git** - For cloning and version control

---

## Step 1: Get OpenAI API Key (5 minutes)

### 1.1 Create OpenAI Account
- Go to https://openai.com/
- Sign up or log in
- Verify your email

### 1.2 Generate API Key
1. Navigate to https://platform.openai.com/api/keys
2. Click **"Create new secret key"**
3. Copy the key (starts with `sk-proj-`)
4. **⚠️ Never share this key or commit it to git**

### 1.3 Verify You Have Credits
- Check https://platform.openai.com/account/billing/overview
- Ensure you have credits or payment method on file

---

## Step 2: Configure Environment (2 minutes)

### 2.1 Copy Environment Template
```bash
cd backend
cp ../.env.example .env
```

### 2.2 Edit .env File
Open `backend/.env` and replace:
```env
OPENAI_API_KEY=sk-proj-your-actual-api-key-here
```

With your actual key:
```env
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**⚠️ IMPORTANT**:
- `.env` file is in `.gitignore` (won't be committed)
- Never share or publish your API key
- Keep `.env` local to your machine only

### 2.3 Verify Other Settings (Optional)
Most settings have good defaults. Adjust only if needed:

```env
# Backend runs on localhost:8000
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

# Frontend communicates from localhost:3000
CORS_ORIGINS=http://localhost:3000

# Use semantic chunking (most accurate)
CHUNKING_STRATEGY=semantic

# Use hybrid search (best accuracy)
SEARCH_TYPE=hybrid
```

---

## Step 3: Install Backend Dependencies (2 minutes)

```bash
cd backend
pip install -r requirements.txt
```

Expected output:
```
Successfully installed fastapi uvicorn pydantic sqlalchemy chromadb openai ...
```

If you get errors:
```bash
# Upgrade pip first
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Step 4: Install Frontend Dependencies (2 minutes)

```bash
cd frontend
npm install
```

Expected output:
```
added 200+ packages
```

If you get errors:
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

---

## Step 5: Start Backend (Terminal 1)

```bash
cd backend
python -m uvicorn app.main:app --reload
```

Expected output:
```
✓ RAG components initialized
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### Troubleshooting

**Error: `ModuleNotFoundError: No module named 'openai'`**
```bash
pip install openai
```

**Error: `Port 8000 already in use`**
```bash
# Find what's using port 8000
lsof -i :8000
# Kill the process or use different port
python -m uvicorn app.main:app --reload --port 8001
```

**Error: `OPENAI_API_KEY not set`**
```bash
# Check your .env file
cat backend/.env | grep OPENAI_API_KEY

# Verify key is not empty
echo $OPENAI_API_KEY
```

---

## Step 6: Start Frontend (Terminal 2)

```bash
cd frontend
npm run dev
```

Expected output:
```
ready - started server on 0.0.0.0:3000
```

If you see errors about Next.js or dependencies:
```bash
# Clear Next.js cache
rm -rf .next
npm run dev
```

---

## Step 7: Open Application

1. Open your browser
2. Go to **http://localhost:3000**
3. You should see the chat interface! 🎉

---

## Step 8: Test RAG System

### Quick Test in UI

1. **Select Department**: Choose "HR" from dropdown
2. **Upload Document**: Click upload, add a sample document
3. **Ask Question**: Type "What is the leave policy?"
4. **See Answer**: RAG system should return an answer with sources ✅

### Test via Terminal

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test RAG endpoint (requires uploaded documents)
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the leave policy?",
    "department": "hr"
  }'
```

---

## Troubleshooting

### Frontend Won't Load

```bash
# Check Node.js version
node --version  # Should be 16+

# Clear cache and reinstall
cd frontend
rm -rf node_modules .next package-lock.json
npm install
npm run dev
```

### Backend Returns 500 Error

```bash
# Check OpenAI API key is set
echo $OPENAI_API_KEY

# Check API key has quotes removed
# ❌ OPENAI_API_KEY="sk-proj-xxx"
# ✅ OPENAI_API_KEY=sk-proj-xxx
```

### RAG Responses Are Slow (> 5 seconds)

- **First query**: Normal (includes LLM call)
- **Repeated query**: Should be 20-100ms faster (cache hit)
- **If still slow**: Check OpenAI API rate limits

### Port Already in Use

```bash
# Find process using the port
lsof -i :3000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use different port
npm run dev -- -p 3001
python -m uvicorn app.main:app --port 8001
```

---

## Configuration Reference

### Core Configuration

| Variable | Default | Purpose |
|----------|---------|---------|
| `OPENAI_API_KEY` | (required) | OpenAI API authentication |
| `BACKEND_HOST` | 0.0.0.0 | Backend server bind address |
| `BACKEND_PORT` | 8000 | Backend server port |
| `CORS_ORIGINS` | localhost:3000 | Frontend URL for CORS |

### RAG Configuration

| Variable | Default | Purpose |
|----------|---------|---------|
| `EMBEDDING_MODEL` | text-embedding-3-small | Embedding model |
| `GENERATION_MODEL` | gpt-3.5-turbo | Chat model (gpt-4 for higher accuracy) |
| `CHUNKING_STRATEGY` | semantic | How to split documents |
| `CHUNK_SIZE` | 500 | Characters per chunk |
| `SEARCH_TYPE` | hybrid | Search method (vector/keyword/hybrid) |
| `TOP_K` | 5 | Number of results to retrieve |
| `ENABLE_CACHE` | true | Cache repeated queries |

---

## Common Issues & Solutions

### Issue: "I cannot find a reliable answer" for all queries

**Solution:**
1. Upload a test document first
2. Wait 2-3 seconds for indexing
3. Ask a question related to the document content
4. Check department matches (HR document → department: hr)

### Issue: OpenAI API returns 401 Unauthorized

**Solution:**
1. Verify API key is correct (copy from openai.com again)
2. Check API key has not expired
3. Ensure you have remaining credits
4. Check `.env` file has correct key (no extra quotes)

### Issue: TypeError: 'NoneType' object is not subscriptable

**Solution:**
- This usually means OpenAI API call failed
- Check your API key and credits
- Verify internet connection
- Check OpenAI API status page

### Issue: Vector store is empty

**Solution:**
1. Upload documents via `/api/documents/upload`
2. Verify files were uploaded: `curl http://localhost:8000/api/stats`
3. Check documents have correct department

---

## Next Steps

After successful setup:

1. **Explore RAG Features**
   - Test different chunking strategies
   - Try hybrid vs. vector-only search
   - Upload multiple document types

2. **Review Documentation**
   - Read `RAG_IMPLEMENTATION.md` for technical details
   - Check `RAG_TESTING_GUIDE.md` for advanced testing

3. **Customize Configuration**
   - Adjust chunk sizes for your documents
   - Try GPT-4 for higher accuracy
   - Configure search weights

4. **Integrate with Your Data**
   - Upload your actual documents
   - Set up department filtering
   - Add custom metadata

5. **Deploy to Production**
   - Switch database from SQLite to PostgreSQL
   - Use Pinecone for vector store
   - Add authentication
   - Set up monitoring

---

## Support

**Having issues?** Check in this order:

1. **This file** - Common issues and solutions
2. **RAG_TESTING_GUIDE.md** - Detailed endpoint testing
3. **FINAL_STATUS.md** - Architecture and design
4. **RAG_IMPLEMENTATION.md** - Technical reference

---

## Environment Setup Summary

```bash
# 1. Create backend/.env from template
cp .env.example backend/.env

# 2. Edit backend/.env with your OpenAI API key
# OPENAI_API_KEY=sk-proj-your-actual-key

# 3. Install dependencies
cd backend && pip install -r requirements.txt
cd ../frontend && npm install

# 4. Start backend (Terminal 1)
cd backend && python -m uvicorn app.main:app --reload

# 5. Start frontend (Terminal 2)
cd frontend && npm run dev

# 6. Open http://localhost:3000 in browser

# 7. Test by uploading a document and asking a question
```

---

**You're ready to use the Enterprise Knowledge Assistant!** 🎉

If you encounter any issues, refer back to this guide or check the documentation files.
