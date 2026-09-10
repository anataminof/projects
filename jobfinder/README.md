# Job Search System (Tasks 1 & 2)

A job-search automation system with two concurrent tasks:
- **Task 1**: Cyclic coverage of a known company database (Careers/ATS sites)
- **Task 2**: Open-web discovery across multiple sources

## Architecture

- **Frontend**: React + TypeScript + Vite
- **Backend**: FastAPI + Python
- **Storage**: SQLite (MVP) → PostgreSQL (V1)
- **Search/Fetch**: Playwright + httpx + BeautifulSoup/lxml
- **AI**: Swappable AIProvider (OllamaProvider for local LLM, OpenAIProvider for cloud)

See [`docs/development_plan.md`](docs/development_plan.md) for the phased development roadmap.

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- pip / npm

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Start the server
uvicorn app.main:app --reload
```

The backend will be available at `http://localhost:8000`.
Health check: `GET http://localhost:8000/health`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:5173`.
The dev server proxies `/api/*` requests to the backend at `http://localhost:8000`.

### Running Both Together (separate terminals)

Terminal 1 — Backend:
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

Terminal 2 — Frontend:
```bash
cd frontend
npm run dev
```

Then visit `http://localhost:5173`.

## Configuration

### Environment Variables

- `DATA_DIR`: Path to external canonical data files (companies, applications history, skills profile)
  - Default: `./data` (relative to backend working directory)
  - Should point to where `tech_companies_master.xlsx`, `job_applications_master.xlsx`, and other canonical files are stored
  - This directory should be gitignored; provide your own copies

### Config Files

Seed configurations (editable, will migrate to DB in Phase 2):
- `config/companies.seed.json` — company list for Task 1
- `config/role_families.json` — job role families (PM, TPM, Release Manager, etc.)
- `config/search_keywords.json` — keywords for job searches (English + Hebrew)
- `config/search_sources.json` — search sources (Greenhouse, Lever, Comeet, Generic Careers)

## Development Phases

1. **Phase 0** ✅ Repo bootstrap (this setup)
2. **Phase 1** — Data model & storage (Job, Run, ApplicationStatus, etc.)
3. **Phase 2** — Config & canonical data loader
4. **Phase 3** — Normalization + Dedup engine
5. **Phase 4** — Application Gate (has-been-applied check)
6. **Phase 5** — AIProvider abstraction + schemas + prompts
7. **Phase 6** — Search/fetch engine + ATS adapters (MVP: Greenhouse, Lever, Comeet, Generic)
8. **Phase 7** — Coverage & retry tracking (basic MVP level)
9. **Phase 8** — Task 1 & Task 2 orchestrators
10. **Phase 9** — FastAPI endpoints
11. **Phase 10** — React UI (Dashboard, Jobs, Run Details screens)
12. **Phase 11** — MVP integration & acceptance tests

See [`docs/development_plan.md`](docs/development_plan.md) for detailed phase descriptions.

## Testing

### Backend

```bash
cd backend
pytest                    # Run all tests
pytest -v               # Verbose output
pytest --cov            # Coverage report
pytest backend/tests/storage/test_models.py  # Single file
```

### Frontend

```bash
cd frontend
npm run type-check      # TypeScript check
npm run lint            # ESLint
```

## Deployment (V1+)

### Local Development

Everything runs on one machine (React dev server, FastAPI local service, SQLite, local Ollama).

### Production (Future)

- Frontend: static build served from a web server
- Backend: containerized FastAPI (Docker)
- Database: PostgreSQL (post-MVP)
- AI: OpenAI API or cloud-hosted Ollama

## Code Structure

```
backend/
  app/
    main.py                 # FastAPI entry point
  storage/                  # Phase 1: data model & persistence
  dedup/                    # Phase 3: normalization & dedup
  applications/             # Phase 4: Application Gate
  ai/                       # Phase 5: AIProvider & schemas
  search/                   # Phase 6: search query builder
  ats/                      # Phase 6: ATS adapters
  tasks/                    # Phase 8: Task 1 & Task 2
  api/                      # Phase 9: FastAPI routers & DTOs
  coverage/                 # Phase 7: coverage & retry tracking
  tests/                    # Unit, integration, fixture tests
config/
  companies.seed.json       # Seed company list
  role_families.json        # Role families
  search_keywords.json      # Search keywords
  search_sources.json       # Search sources
frontend/
  src/
    pages/                  # Phase 10: Dashboard, Jobs, RunDetails
    api/                    # API client
    components/             # Reusable components
    types/                  # TypeScript types
    App.tsx                 # Main app component
    main.tsx                # Entry point
docs/
  development_plan.md       # Detailed phased plan
```

## Contact & Questions

See the spec: `job_search_tasks_1_2_architecture_he_v5.md`

---

*Generated with [Claude Code](https://claude.com/claude-code)*
