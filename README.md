# CACI Mission Intake and Analysis Copilot

An ESF-aligned AI accelerator for mission document analysis with LLM-assisted summarization, entity extraction, risk classification, and cost transparency.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![React](https://img.shields.io/badge/react-18+-blue.svg)

## 🎯 Project Overview

This lightweight accelerator demonstrates rapid time-to-value by ingesting messy mission inputs (PDFs, CSVs, TXT files, and free text), normalizing them, applying LLM-assisted analysis, persisting structured results, and presenting explainable outputs in a responsive web dashboard with explicit cost transparency.

**This is intentionally not a production system.** It is a high-leverage Enterprise Solutions Factory (ESF) accelerator designed to:

- ✅ Deliver a strong 60-75% solution
- ✅ Demonstrate reuse, clarity, and explainability
- ✅ Treat AI as an assistive capability, not an authority
- ✅ Include explicit cost transparency
- ✅ Support human-in-the-loop decision making

## 📸 Screenshots

### Mission Intake
Upload documents (PDF, CSV, TXT) via drag-and-drop or submit free-text. Features auto-analyze toggle for streamlined processing.

![Mission Intake](docs/screenshots/mission_intake.jpg)

### Mission Registry
Track all ingested missions with status badges, document types, and quick actions. Real-time stats show total, analyzed, and pending counts.

![Mission Registry](docs/screenshots/mission_registry.jpg)

### Analysis Results
View AI-generated summaries, risk classification, and extracted entities alongside the original document. Includes cost transparency with token usage and processing time.

![Analysis Results](docs/screenshots/analysis_results.jpg)

### Executive Dashboard
Clean, scannable overview for leadership. Key metrics at a glance, attention items highlighted, and recent activity tracking.

![Dashboard](docs/screenshots/dashboard.png)

## 🏗️ Architecture

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   React Frontend │────▶│   FastAPI Backend│────▶│   SQLite/        │
│   (Vite)         │     │   + AI Services  │     │   PostgreSQL     │
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
- **TXT Upload**: Upload plain text intelligence documents
- **Free Text**: Submit analyst notes, emails, or summaries directly

### AI-Assisted Analysis
- **Summarization**: Concise 3-5 sentence mission summaries
- **Entity Extraction**: Identify people, organizations, systems, risks
- **Risk Classification**: LOW / MEDIUM / HIGH / CRITICAL assessment
- **Explanations**: Natural language insights for decision makers

### Cost Transparency
- Token usage tracking for every analysis
- Estimated cost display (Hugging Face free tier = $0)
- Audit trail in database

### Human-in-the-Loop
- Analyst review workflow
- Approval/rejection with notes
- All AI content clearly labeled

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Hugging Face API key (free tier) - *optional for demo*

### Option 1: Local Development (SQLite - Easiest)

The application defaults to **SQLite** for zero-configuration setup. No Docker or PostgreSQL required!

```bash
# Clone repository
git clone https://github.com/michaelromero212/CACI-Mission-Intake-and-Analysis-Copilot.git
cd CACI-Mission-Intake-and-Analysis-Copilot

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start backend (creates mission_copilot.db automatically)
./venv/bin/python -m uvicorn main:app --reload --port 8000

# In a new terminal - Frontend setup
cd frontend
npm install
npm run dev
```

**Access the app at:** http://localhost:5173

### Option 2: PostgreSQL with Docker

For production-like setup with PostgreSQL:

```bash
# Copy environment template
cp .env.template .env

# Edit .env and set:
# DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/mission_copilot

# Start PostgreSQL
docker-compose up -d

# Then follow backend/frontend steps above
```

### Option 3: External PostgreSQL

Set the `DATABASE_URL` environment variable to your PostgreSQL connection string:

```bash
export DATABASE_URL="postgresql+asyncpg://user:password@host:5432/database"
```

## 🔑 Enabling AI Analysis

To use AI analysis features, get a free Hugging Face API key:

1. Sign up at https://huggingface.co
2. Go to Settings → Access Tokens
3. Create a new token

```bash
# Create .env file in backend/
echo "HUGGINGFACE_API_KEY=hf_your_key_here" > backend/.env
```

Without an API key, the app still works for document ingestion and storage.

## 📁 Repository Structure

```
CACI-Mission-Intake-and-Analysis-Copilot/
├── .github/workflows/    # CI/CD pipeline
│   └── ci.yml            # GitHub Actions workflow
├── backend/
│   ├── api/              # FastAPI route handlers
│   ├── services/         # Business logic layer
│   ├── ingestion/        # Document parsers (PDF, CSV, TXT)
│   ├── ai/               # LLM and RAG services
│   ├── models/           # SQLAlchemy ORM models
│   ├── db/               # Database configuration
│   ├── tests/            # pytest test suite
│   ├── main.py           # FastAPI application entry
│   └── config.py         # Settings (SQLite default)
├── frontend/
│   └── src/
│       ├── components/   # Reusable React components
│       ├── pages/        # Page-level components
│       ├── api.js        # Backend API client
│       └── index.css     # CACI light theme design system
├── scripts/              # Automation scripts
│   └── batch_analyze.py  # Bulk document processor
├── prompts/              # LLM prompt templates
├── sample_data/          # DoD/Intelligence test documents
├── docs/                 # Documentation + screenshots
├── Dockerfile            # Container build
├── docker-compose.yml    # PostgreSQL setup (optional)
├── .env.template         # Environment template
└── README.md
```

## 📊 Database Schema

The application uses SQLAlchemy ORM with support for both SQLite and PostgreSQL.

### missions
| Column | Type | Description |
|--------|------|-------------|
| mission_id | String(36) | UUID primary key |
| source_type | String | pdf, csv, text |
| filename | VARCHAR | Original filename |
| status | String | pending, ingested, analyzing, analyzed, error |
| normalized_content | TEXT | Processed content |
| mission_metadata | JSON | Source-specific metadata |
| ingestion_timestamp | TIMESTAMP | When ingested |

### analysis_results
| Column | Type | Description |
|--------|------|-------------|
| analysis_id | String(36) | UUID primary key |
| mission_id | String(36) | Foreign key to missions |
| summary_text | TEXT | AI-generated summary |
| extracted_entities | JSON | Structured entity list |
| risk_level | String | low, medium, high, critical |
| total_tokens | INT | Token count |
| estimated_cost | FLOAT | Cost estimate |

### analyst_reviews
| Column | Type | Description |
|--------|------|-------------|
| review_id | String(36) | UUID primary key |
| mission_id | String(36) | Foreign key to missions |
| analyst_notes | TEXT | Human feedback |
| approved | BOOLEAN | Approval status |

## 🧪 Sample Data

The `sample_data/` directory includes realistic DoD/Intelligence documents:

| File | Description |
|------|-------------|
| `intel_collection_requirements.txt` | DIA collection requirements document |
| `sigint_analyst_summary.txt` | SIGINT analyst daily shift report |
| `threat_assessment.csv` | Multi-threat assessment matrix |
| `personnel_clearance_roster.csv` | Clearance and polygraph tracking |
| `contract_performance_report.txt` | Contract status and CDRLs |
| `risk_register.csv` | Project risks with mitigations |
| `task_list.csv` | Project task dependencies |
| `analyst_notes.txt` | Free-form technical observations |
| `mission_summary.txt` | Formal mission overview |

## 🔄 Example Workflow

1. **Upload**: Navigate to http://localhost:5173 and upload a CSV, TXT, or PDF
2. **Ingest**: Document is parsed, normalized, and stored
3. **Analyze**: Click "Run AI Analysis" for summarization and entity extraction
4. **Review**: Add analyst notes and approve or reject the analysis

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

## 🧪 Testing

Run the test suite with pytest:

```bash
cd backend
pip install -r requirements.txt  # Includes pytest
python -m pytest tests/ -v
```

With coverage report:

```bash
python -m pytest tests/ -v --cov=. --cov-report=term-missing
```

## 🐳 Docker

Build and run with Docker:

```bash
# Build image
docker build -t caci-mission-copilot .

# Run container
docker run -p 8000:8000 -e HUGGINGFACE_API_KEY=your_key caci-mission-copilot

# Access API at http://localhost:8000
```

## 🤖 Automation

### Batch Processing Script

Process multiple documents automatically:

```bash
# Process all files in sample_data/
python scripts/batch_analyze.py --input ./sample_data --output ./reports

# Skip AI analysis (ingestion only)
python scripts/batch_analyze.py --input ./data --skip-analysis
```

The script generates JSON and CSV reports with processing results.

## 🔄 CI/CD

GitHub Actions workflow (`.github/workflows/ci.yml`) runs on every push:

- **Backend Tests**: pytest with coverage
- **Backend Lint**: ruff linter
- **Frontend Build**: npm build verification
- **Docker Build**: Dockerfile validation

## 🎨 Design Philosophy

See [docs/design_decisions.md](docs/design_decisions.md) for detailed rationale on:

- Why Hugging Face over OpenAI
- SQLite default for easy development
- PostgreSQL support for production
- FAISS vs Chroma for RAG
- Light theme with CACI branding
- Government/Intelligence UI patterns

## 📜 License

This project is provided as an ESF accelerator demonstration. See LICENSE for details.

---

**Built with ❤️ following ESF principles: Execution over perfection.**
