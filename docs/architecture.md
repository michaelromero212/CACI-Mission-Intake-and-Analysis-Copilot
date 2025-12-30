# System Architecture

## Overview

The CACI Mission Intake and Analysis Copilot follows a three-tier architecture pattern, optimized for rapid development and demonstrability while maintaining clear separation of concerns.

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend                                 │
│                    (React + Vite)                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Mission      │  │ Analysis     │  │ Mission              │  │
│  │ Intake Page  │  │ Results Page │  │ History Page         │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────┬───────────────────────────────────────┘
                          │ HTTP/REST API
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Backend                                   │
│                      (FastAPI)                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    API Layer                              │  │
│  │  /api/missions  │  /api/analysis  │  /api/reviews        │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  Services Layer                           │  │
│  │  mission_service  │  analysis_service                     │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    AI Layer                               │  │
│  │  llm_client  │  analyzer  │  rag_service  │  cost_tracker │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │               Ingestion Layer                             │  │
│  │  pdf_parser  │  csv_parser  │  text_parser  │  normalizer │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────┬───────────────────────────────────────┘
                          │ SQLAlchemy ORM
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Data Layer                                  │
│  ┌─────────────────┐              ┌──────────────────────────┐  │
│  │   PostgreSQL    │              │    FAISS Vector Store    │  │
│  │  - missions     │              │    (In-Memory/Local)     │  │
│  │  - analysis     │              └──────────────────────────┘  │
│  │  - reviews      │                                            │
│  └─────────────────┘              ┌──────────────────────────┐  │
│                                   │  Hugging Face API        │  │
│                                   │  (External LLM)          │  │
│                                   └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### Frontend (React)

| Component | Purpose |
|-----------|---------|
| `MissionIntake` | File upload and text submission |
| `AnalysisResults` | Display AI analysis with cost transparency |
| `MissionHistory` | PostgreSQL-backed mission list |
| `AnalysisCard` | Render AI output with labels |
| `CostDisplay` | Token usage and cost visualization |

### Backend (FastAPI)

| Layer | Components |
|-------|------------|
| **API** | missions.py, analysis.py, reviews.py |
| **Services** | mission_service.py, analysis_service.py |
| **Ingestion** | pdf_parser, csv_parser, text_parser, normalizer |
| **AI** | llm_client, analyzer, rag_service, cost_tracker |
| **Data** | SQLAlchemy models, async PostgreSQL driver |

### Data Flow

1. **Ingestion**: User uploads file → Parser extracts content → Normalizer creates standard schema → Mission saved to PostgreSQL
2. **Analysis**: User triggers analysis → RAG retrieves context → LLM generates analysis → Results saved with cost data
3. **Review**: Analyst views results → Adds notes → Approves/rejects → Review state persisted

## External Dependencies

| Service | Purpose | Configuration |
|---------|---------|---------------|
| PostgreSQL | Relational data persistence | `DATABASE_URL` |
| Hugging Face | LLM inference API | `HUGGINGFACE_API_KEY` |
| Sentence Transformers | Local embeddings | Downloaded on first use |
| FAISS | Vector similarity search | In-memory storage |
