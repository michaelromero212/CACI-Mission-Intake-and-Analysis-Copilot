# CACI Mission Intake and Analysis Copilot

An ESF-aligned AI accelerator for mission document analysis with LLM-assisted summarization, entity extraction, risk classification, and cost transparency.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![React](https://img.shields.io/badge/react-18+-blue.svg)

## 🎯 Project Overview

This lightweight accelerator demonstrates rapid time-to-value by ingesting messy mission inputs (PDFs, CSVs, and free text), normalizing them, applying LLM-assisted analysis, persisting structured results in PostgreSQL, and presenting explainable outputs in a responsive web dashboard with explicit cost transparency.

**This is intentionally not a production system.** It is a high-leverage Enterprise Solutions Factory (ESF) accelerator designed to:

- ✅ Deliver a strong 60-75% solution
- ✅ Demonstrate reuse, clarity, and explainability
- ✅ Treat AI as an assistive capability, not an authority
- ✅ Include explicit cost transparency
- ✅ Support human-in-the-loop decision making

## 🏗️ Architecture

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   React Frontend │────▶│   FastAPI Backend│────▶│   PostgreSQL     │
│   (Vite)         │     │   + AI Services  │     │   Database       │
└──────────────────┘     └──────────────────┘     └──────────────────┘
                                  │
                         ┌───────┴───────┐
                         ▼               ▼
                  ┌────────────┐  ┌────────────┐
                  │ Hugging    │  │ FAISS      │
                  │ Face API   │  │ (RAG)      │
                  └────────────┘  └────────────┘
```

See [docs/architecture.md](docs/architecture.md) for detailed component diagrams.

## ✨ Features

### Document Ingestion
- **PDF Upload**: Extract text and metadata from PDF documents
- **CSV Upload**: Parse structured data with automatic schema detection
- **Free Text**: Submit analyst notes, emails, or summaries directly

### AI-Assisted Analysis
- **Summarization**: Concise 3-5 sentence mission summaries
- **Entity Extraction**: Identify people, organizations, systems, risks
- **Risk Classification**: LOW / MEDIUM / HIGH / CRITICAL assessment
- **Explanations**: Natural language insights for decision makers

### Cost Transparency
- Token usage tracking for every analysis
- Estimated cost display (Hugging Face free tier = $0)
- Audit trail in PostgreSQL

### Human-in-the-Loop
- Analyst review workflow
- Approval/rejection with notes
- All AI content clearly labeled

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ (or Docker)
- Hugging Face API key (free tier)

### 1. Clone and Setup

```bash
git clone https://github.com/your-org/CACI-Mission-Intake-and-Analysis-Copilot.git
cd CACI-Mission-Intake-and-Analysis-Copilot

# Copy environment template
cp .env.template .env
# Edit .env with your Hugging Face API key
```

### 2. Start PostgreSQL

```bash
# Using Docker
docker-compose up -d

# Or use local PostgreSQL and update DATABASE_URL in .env
```

### 3. Install Backend Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Start Backend

```bash
cd backend
uvicorn main:app --reload
# API available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### 5. Install and Start Frontend

```bash
cd frontend
npm install
npm run dev
# App available at http://localhost:5173
```

## 📁 Repository Structure

```
CACI-Mission-Intake-and-Analysis-Copilot/
├── backend/
│   ├── api/              # FastAPI route handlers
│   ├── services/         # Business logic layer
│   ├── ingestion/        # Document parsers
│   ├── ai/               # LLM and RAG services
│   ├── models/           # SQLAlchemy ORM models
│   ├── db/               # Database configuration
│   ├── main.py           # FastAPI application entry
│   └── config.py         # Settings management
├── frontend/
│   └── src/
│       ├── components/   # Reusable React components
│       ├── pages/        # Page-level components
│       ├── api.js        # Backend API client
│       └── index.css     # CACI design system
├── prompts/              # LLM prompt templates
├── sample_data/          # Test documents
├── docs/                 # Documentation
├── docker-compose.yml    # PostgreSQL setup
├── .env.template         # Environment template
└── README.md
```

## 📊 Database Schema

### missions
| Column | Type | Description |
|--------|------|-------------|
| mission_id | UUID | Primary key |
| source_type | ENUM | pdf, csv, text |
| filename | VARCHAR | Original filename |
| status | ENUM | pending, ingested, analyzing, analyzed, error |
| normalized_content | TEXT | Processed content |
| metadata | JSON | Source-specific metadata |
| ingestion_timestamp | TIMESTAMP | When ingested |

### analysis_results
| Column | Type | Description |
|--------|------|-------------|
| analysis_id | UUID | Primary key |
| mission_id | UUID | Foreign key to missions |
| summary_text | TEXT | AI-generated summary |
| extracted_entities | JSON | Structured entity list |
| risk_level | ENUM | low, medium, high, critical |
| total_tokens | INT | Token count |
| estimated_cost | FLOAT | Cost estimate |

### analyst_reviews
| Column | Type | Description |
|--------|------|-------------|
| review_id | UUID | Primary key |
| mission_id | UUID | Foreign key to missions |
| analyst_notes | TEXT | Human feedback |
| approved | BOOLEAN | Approval status |

## 🔄 Example Workflow

### 1. Upload Sample Data

```bash
# Navigate to the app
open http://localhost:5173

# Upload sample_data/risk_register.csv via the UI
```

### 2. Run Analysis

Click "Run AI Analysis" to generate:
- Summary of the risk register
- Extracted entities (risks, owners, dates)
- Overall risk classification
- Cost transparency data

### 3. Review and Approve

- View AI-generated content (clearly labeled)
- Add analyst notes
- Approve or request re-analysis

## 💰 Cost Transparency

This accelerator tracks and displays:

| Metric | Description |
|--------|-------------|
| Input Tokens | Tokens sent to the LLM |
| Output Tokens | Tokens generated by the LLM |
| Total Tokens | Combined token count |
| Estimated Cost | Dollar estimate (free tier = $0) |
| Model Used | Which LLM processed the request |

## 🚫 Explicit Non-Goals

The following are **intentionally not implemented**:

- ❌ Authentication or authorization
- ❌ User management
- ❌ Production security hardening
- ❌ Model training or fine-tuning
- ❌ Kubernetes or complex infrastructure
- ❌ Large-scale data pipelines

## 🎨 Design Philosophy

See [docs/design_decisions.md](docs/design_decisions.md) for detailed rationale on:

- Why Hugging Face over OpenAI
- PostgreSQL async patterns
- FAISS vs Chroma for RAG
- Heuristic confidence indicators
- Light theme only

## 🧪 Testing with Sample Data

The `sample_data/` directory includes:

| File | Description |
|------|-------------|
| `task_list.csv` | Project task data with dependencies |
| `risk_register.csv` | Risk items with mitigations |
| `analyst_notes.txt` | Free-form technical observations |
| `mission_summary.txt` | Formal mission overview document |

## 📜 License

This project is provided as an ESF accelerator demonstration. See LICENSE for details.

---

**Built with ❤️ following ESF principles: Execution over perfection.**
