# Enterprise Knowledge Assistant - Quick Start Guide

## 🚀 Start the Application (2 minutes)

### Prerequisites
- Python 3.9+
- Node.js 16+
- OpenAI API key

### Step 1: Install Dependencies

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

### Step 2: Set Environment Variables

```bash
export OPENAI_API_KEY="sk-your-key-here"
export CORS_ORIGINS="http://localhost:3000"
```

### Step 3: Start Backend (Terminal 1)

```bash
cd backend
python -m uvicorn app.main:app --reload
```

Should show:
```
✓ RAG components initialized
Uvicorn running on http://0.0.0.0:8000
```

### Step 4: Start Frontend (Terminal 2)

```bash
cd frontend
npm run dev
```

Should show:
```
ready - started server on 0.0.0.0:3000
```

### Step 5: Open Browser

Go to **http://localhost:3000** 🎉

---

## 📚 Test RAG System (5 minutes)

### 1. Upload Test Document

```bash
# Create test file
cat > /tmp/leave_policy.txt << 'EOF'
EMPLOYEE LEAVE POLICY

All full-time employees are entitled to 20 working days of paid annual leave.

Additional entitlements:
- Senior employees (5+ years): +5 days
- Managers (3+ years): +3 days

Leave Request Procedure:
1. Submit at least 2 weeks in advance
2. Use HR portal or email manager
3. Approval based on team requirements
