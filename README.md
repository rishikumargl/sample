# Enterprise Knowledge Assistant

A production-ready RAG (Retrieval-Augmented Generation) assistant for enterprise knowledge management.

## Features

- **Multi-Department Support**: Engineering, HR, Operations, Product
- **Vector Search**: ChromaDB with sentence-transformers
- **Hybrid Search**: Vector + BM25 keyword matching
- **Document Processing**: PDF, Word, Markdown support
- **LLM Integration**: OpenAI GPT-4
- **Source Attribution**: Every response includes sources
- **Hallucination Control**: Confidence thresholds and validation

## Tech Stack

### Backend
- FastAPI (async REST API)
- SQLAlchemy (ORM)
- ChromaDB (vector database)
- LangChain (RAG framework)
- OpenAI API

### Frontend
- Next.js 14
- React 18
- TypeScript
- Tailwind CSS

### DevOps
- Docker & Docker Compose
- PostgreSQL
- Python 3.9+, Node.js 16+

## Quick Start

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Docker
```bash
docker-compose up --build
```

## Project Structure

```
backend/
  ├── app/
  │   ├── api/          # API routes
  │   ├── main.py       # FastAPI app
  │   ├── config.py     # Configuration
  │   ├── models.py     # Pydantic schemas
  │   └── database.py   # SQLAlchemy setup
  └── requirements.txt  # 42 Python packages

frontend/
  ├── src/
  │   ├── components/   # React components
  │   ├── pages/        # Next.js pages
  │   ├── hooks/        # Custom hooks
  │   ├── utils/        # API client
  │   ├── types/        # TypeScript types
  │   └── styles/       # CSS
  └── package.json      # 22 JavaScript packages
```

## Dependencies

**Backend**: 42 Python packages
- FastAPI, Uvicorn, Pydantic
- SQLAlchemy, PostgreSQL
- LangChain, OpenAI, ChromaDB
- PyPDF2, python-docx, NLTK
- pytest, black, flake8, mypy

**Frontend**: 22 JavaScript packages
- React, Next.js, TypeScript
- Tailwind CSS, Axios
- react-markdown, lucide-react

See [DEPENDENCIES.md](DEPENDENCIES.md) for details.

## Team Workflow

5-member team structure:

1. **Member 1**: Backend API (`feature/backend-api-setup`)
2. **Member 2**: Frontend Components (`feature/frontend-components`)
3. **Member 3**: Frontend API Client (`feature/frontend-api-client`)
4. **Member 4**: Document Processing (`feature/rag-document-processing`)
5. **Member 5**: RAG Pipeline (`feature/rag-retrieval-llm`)

See [TEAM_TASK_DIVISION.md](TEAM_TASK_DIVISION.md) for detailed assignments.

## API Endpoints

- `GET /health` - Health check
- `POST /api/chat` - Chat with RAG
- `POST /api/documents/upload` - Upload document
- `GET /api/documents` - List documents
- `GET /api/documents/{id}` - Get document
- `DELETE /api/documents/{id}` - Delete document

## Documentation

- [README.md](README.md) - Project overview
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [SETUP.md](SETUP.md) - Detailed setup guide
- [DEPENDENCIES.md](DEPENDENCIES.md) - Package documentation
- [TEAM_TASK_DIVISION.md](TEAM_TASK_DIVISION.md) - Team assignments
- [CONTRIBUTING.md](CONTRIBUTING.md) - Development workflow

## Environment Variables

See [.env.example](.env.example) for all variables.

Key variables:
```
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
DATABASE_URL=sqlite:///./enterprise_rag.db
OPENAI_API_KEY=your_key_here
```

## Development

### Git Workflow
```bash
git checkout -b feature/your-feature
# Make changes
git add .
git commit -m "feat(scope): description"
git push origin feature/your-feature
```

### Code Quality
```bash
# Backend
black backend/
flake8 backend/
mypy backend/

# Frontend
npm run lint
npm run type-check
```

## Testing

```bash
# Backend
pytest backend/tests/

# Frontend
npm test
```

## Deployment

### Docker Compose
```bash
docker-compose up --build
```

### Production
See [SETUP.md](SETUP.md) for production deployment guide.

## License

Proprietary - Enterprise Use Only

## Support

- Documentation: See files in repository
- Issues: GitHub Issues
- Discussion: GitHub Discussions

---

**Status**: Foundation complete, ready for RAG implementation
**Last Updated**: June 3, 2026
**Version**: 1.0.0
