# Local Development Guide

## Quick Start

### Option 1: Automated (Recommended)

```bash
# Start both backend and frontend
./start-dev.sh

# In another terminal, to stop:
./stop-dev.sh
```

### Option 2: Manual

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
pip install -e .  # First time only
uvicorn app.main:app --reload
```

Backend will run on: `http://localhost:8000`

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install  # First time only
npm run dev
```

Frontend will run on: `http://localhost:5173`

---

## What Each Service Does

### Backend (FastAPI)
- **Port**: 8000
- **Endpoints**:
  - `GET /` - Root endpoint
  - `GET /health` - Health check
  - `POST /api/runs/task1` - Start Task 1
  - `POST /api/runs/task2` - Start Task 2
  - `GET /api/runs/{run_id}` - Get run status
  - `GET /api/jobs` - List jobs (with pagination/filtering)
  - `GET /api/jobs/{job_id}` - Get job details
  - `GET /api/dashboard` - Dashboard metrics
- **Docs**: http://localhost:8000/docs (Swagger UI)
- **Code**: `backend/app/`
- **Tests**: `backend/tests/` (run with `pytest tests/ -v`)

### Frontend (React + Vite)
- **Port**: 5173
- **Screens**:
  - Dashboard: Start tasks, view metrics, recent runs
  - Jobs: Browse discovered jobs with filters
  - Run Details: Monitor real-time progress
- **API Client**: `src/api/client.ts`
- **Code**: `frontend/src/`

---

## Environment Variables

### Frontend (.env or Vite config)
```
VITE_API_URL=http://localhost:8000/api
```
(Default is already configured in `vite.config.ts`)

### Backend (env vars, optional)
```
PYTHONUNBUFFERED=1  # Unbuffered Python output
```

---

## Common Tasks

### Run Backend Tests
```bash
cd backend
source venv/bin/activate
pytest tests/ -v                 # All tests
pytest tests/api/ -v             # Only API tests
pytest tests/storage/ -v         # Only storage tests
pytest -k "test_name" -v         # Single test
```

### Build Frontend for Production
```bash
cd frontend
npm run build
npm run preview  # Preview production build
```

### Type Check Frontend
```bash
cd frontend
npm run type-check
```

### Lint Frontend
```bash
cd frontend
npm run lint
```

---

## Troubleshooting

### Backend won't start
- Check if port 8000 is already in use: `lsof -i :8000`
- Kill it: `lsof -ti:8000 | xargs kill -9`
- Check Python version: `python --version` (should be 3.9+)
- Reinstall dependencies: `cd backend && pip install -e .`

### Frontend won't start
- Check if port 5173 is already in use: `lsof -i :5173`
- Kill it: `lsof -ti:5173 | xargs kill -9`
- Clear cache: `rm -rf node_modules package-lock.json && npm install`

### API requests failing from frontend
- Check backend is running: `curl http://localhost:8000/health`
- Check CORS is enabled: Should see CORS headers in response
- Check frontend is using correct API URL (should auto-proxy via Vite)

### Tests failing
- Make sure you're in virtual environment: `source venv/bin/activate`
- Database might be locked: Delete `backend/jobfinder.db` and rerun tests
- Run tests with fresh DB: `rm -f backend/jobfinder.db && pytest tests/`

---

## Development Workflow

1. **Edit backend code** → Auto-reloads with `uvicorn --reload`
2. **Edit frontend code** → Auto-reloads with Vite HMR
3. **Run tests** → Verify changes with `pytest` (backend) or manual testing (frontend)
4. **Commit changes** → `git add` and `git commit`
5. **Push to GitHub** → `git push origin main`

---

## Architecture Overview

```
Frontend (localhost:5173)
    ↓
API Client (src/api/client.ts)
    ↓
Backend API (localhost:8000)
    ├─ Orchestrators (Task 1 & Task 2)
    ├─ Job Discovery (Search/ATS adapters)
    ├─ Deduplication
    ├─ Application Gate
    ├─ AI Integration
    └─ Database (SQLite)
```

---

## Next Steps

After testing locally:
1. Run full test suite: `pytest tests/ -v`
2. Build frontend: `npm run build`
3. Deploy to staging environment
4. Run acceptance tests
5. Deploy to production

---

## Need Help?

- Backend questions: Check `backend/README.md` or `docs/PHASE_COMPLETION_SUMMARY.md`
- Frontend questions: Check component files in `frontend/src/pages/`
- Architecture questions: See `docs/architecture_diagram.html`
