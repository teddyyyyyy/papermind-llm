# 📄 Papermind

> Upload research papers and ask questions about them using AI — powered by RAG, pgvector, and OpenAI.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-backend-green)
![Next.js](https://img.shields.io/badge/Next.js-16-black)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-pgvector-blue)
![Tests](https://img.shields.io/badge/tests-52%20passing-brightgreen)

---

## ✨ Features

- 📂 **Upload PDF or TXT** research papers via drag & drop
- 🤖 **AI-extracted title & summary** generated automatically on upload
- 💬 **RAG-powered Q&A** — ask anything about the paper, answers grounded in the document
- 🗂️ **Drag-and-drop categories** — organise papers into custom categories
- ✏️ **Inline category editing** — rename categories directly in the UI
- 🗑️ **Delete papers and categories** with one click
- ⚙️ **Background worker** — processing happens automatically after upload
- ⚡ **Batch embeddings** — all chunks embedded in one API call for fast processing

---

## 🏗️ Architecture

```
┌─────────────────┐        ┌──────────────────────────────────┐
│   Next.js 16    │  HTTP  │         FastAPI Backend           │
│   (frontend)    │◄──────►│                                   │
│   Vercel        │        │  ┌─────────┐   ┌──────────────┐  │
└─────────────────┘        │  │ Worker  │   │  RAG Service │  │
                           │  │(thread) │   │  (pgvector)  │  │
                           │  └────┬────┘   └──────┬───────┘  │
                           │       │                │          │
                           └───────┼────────────────┼──────────┘
                                   │                │
                           ┌───────▼────────────────▼──────────┐
                           │     PostgreSQL + pgvector          │
                           │   (Docker locally / Supabase prod) │
                           └────────────────────────────────────┘
```

### Upload → Processing flow

```
User uploads PDF/TXT
        │
        ▼
FastAPI saves file + creates Job (status: pending)
        │
        ▼
Background worker picks up job
        │
        ├─► OpenAI extracts title + summary
        │
        └─► Text is chunked → embedded (text-embedding-3-small) → stored in pgvector
                │
                ▼
        Job status → "finished"
                │
                ▼
        User asks a question
                │
                ▼
        Question embedded → top-5 chunks retrieved via cosine similarity
                │
                ▼
        GPT answers using only retrieved context
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 16, TypeScript, Tailwind CSS v4, @dnd-kit |
| Backend | FastAPI, SQLAlchemy, Python 3.11 |
| Database | PostgreSQL 15 + pgvector extension |
| AI / LLM | OpenAI `gpt-5.4-mini` + `text-embedding-3-small` |
| Background jobs | Python threading (auto-started via FastAPI lifespan) |
| Testing | pytest, pytest-mock, httpx (52 tests, SQLite in-memory) |
| CI/CD | GitHub Actions → Render (backend) + Vercel (frontend) |

---

## 🚀 Running locally

### Prerequisites

- Python 3.11 (conda env `mini-rag-py311`)
- Node.js 20+
- Docker Desktop
- OpenAI API key

### 1. Start the database

```bash
cd backend
docker compose up -d
```

This starts `pgvector/pgvector:pg15` on port **5555**.

### 2. Start the backend

```bash
conda activate mini-rag-py311
cd backend
pip install -r requirements.txt
export OPENAI_API_KEY="sk-..."
uvicorn app.main:app --reload
```

API runs at **http://localhost:8000**

### 3. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

App runs at **http://localhost:3000**

---

## 🧪 Running tests

Tests use SQLite in-memory — **no Docker or OpenAI key needed**.

```bash
conda activate mini-rag-py311
cd backend
pytest -v
```

```
52 passed in 0.68s
```

### Test coverage

| File | What's tested |
|---|---|
| `test_job_service.py` | Create, get, delete jobs + chunk cleanup |
| `test_category_service.py` | Create, rename, delete categories + job unassign |
| `test_jobs_router.py` | All `/jobs` endpoints, upload, Q&A (OpenAI mocked) |
| `test_categories_router.py` | All `/categories` endpoints |
| `test_rag_service.py` | `chunk_text` logic — overlap, empty input, boundaries |

---

## 📡 API Endpoints

### Jobs

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/jobs` | Upload a PDF or TXT file |
| `GET` | `/jobs` | List all jobs |
| `GET` | `/jobs/{id}` | Get job status + summary |
| `PATCH` | `/jobs/{id}` | Assign/unassign a category |
| `DELETE` | `/jobs/{id}` | Delete job + chunks + file |
| `POST` | `/jobs/{id}/ask` | Ask a question (RAG) |

### Categories

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/categories` | List all categories |
| `POST` | `/categories` | Create a category |
| `PATCH` | `/categories/{id}` | Rename or recolor |
| `DELETE` | `/categories/{id}` | Delete (papers move to Uncategorized) |

---

## 📁 Project Structure

```
papermind-llm/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app + lifespan worker
│   │   ├── config/database.py      # SQLAlchemy engine + session
│   │   ├── models/
│   │   │   ├── inference_job.py    # Job table (title, status, summary, category_id)
│   │   │   ├── document_chunk.py   # Chunk table (content + Vector(1536))
│   │   │   └── category.py         # Category table (name, color)
│   │   ├── routers/
│   │   │   ├── jobs.py             # /jobs endpoints
│   │   │   └── categories.py       # /categories endpoints
│   │   ├── services/
│   │   │   ├── job_service.py      # Job CRUD
│   │   │   ├── category_service.py # Category CRUD
│   │   │   └── rag_service.py      # Chunking, embedding, similarity search
│   │   └── worker/job_worker.py    # Background processing thread
│   ├── tests/                      # 52 pytest tests
│   ├── docker-compose.yml          # pgvector/pgvector:pg15 on port 5555
│   └── requirements.txt
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx                # Home: upload + category board
│   │   └── jobs/[id]/page.tsx      # Job detail: status, summary, Q&A
│   ├── components/
│   │   ├── CategoryBoard.tsx       # Drag-and-drop board (dnd-kit)
│   │   ├── CategorySection.tsx     # Droppable category with inline rename
│   │   ├── PaperCard.tsx           # Draggable paper card
│   │   ├── FileUpload.tsx          # Drag-and-drop file uploader
│   │   ├── QAInterface.tsx         # Chat-style Q&A
│   │   └── StatusBadge.tsx         # pending / running / finished / failed
│   └── lib/api.ts                  # All API calls
│
└── .github/workflows/
    ├── backend-ci.yml              # pytest on every push
    ├── frontend-ci.yml             # next build on every push
    └── deploy.yml                  # auto-deploy to Render + Vercel
```

---

## 🗺️ Roadmap

- [x] FastAPI backend with PostgreSQL + pgvector
- [x] Background worker (auto-started via lifespan)
- [x] RAG pipeline — chunking, embedding, cosine similarity search
- [x] AI title + summary extraction
- [x] Next.js frontend — upload, Q&A, drag-and-drop categories
- [x] pytest suite (52 tests)
- [x] GitHub Actions CI/CD
- [ ] Migrate DB to Supabase
- [ ] Deploy backend to Render
- [ ] Deploy frontend to Vercel
- [ ] Multi-paper Q&A

---

## 🔐 Environment Variables

| Variable | Required | Description |
|---|---|---|
| `OPENAI_API_KEY` | ✅ | Your OpenAI API key |

Database connection is hardcoded in `backend/app/config/database.py` for local dev. Update to use `DATABASE_URL` env var before deploying.

---

## 💡 RAG Tips

The Q&A uses **Retrieval-Augmented Generation** — it finds the 5 most relevant chunks and sends them to GPT. This means:

| Works well | Doesn't work well |
|---|---|
| "What is the main contribution?" | "How many references?" |
| "What methodology was used?" | "What is on page 5?" |
| "What were the key findings?" | "Summarize every section" |
| "What are the limitations?" | Counting anything |
