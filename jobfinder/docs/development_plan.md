# Job Search System (Tasks 1 & 2) — Phased Development Plan

## Context

The repo (`/Users/anataminof/repositories/projects/jobfinder`) currently contains only the architecture/spec document `job_search_tasks_1_2_architecture_he_v5.md` — no code, no scaffolding. That spec defines two related job-search automation tasks (Task 1: cyclic coverage of a known company database; Task 2: broad open-web discovery) sharing policy, candidate profile, keywords, application history, and a discovery ledger. It mandates a specific architecture (React+TS+Vite client, FastAPI+Python server, SQLite storage, Playwright/httpx fetching, a swappable local-Ollama `AIProvider`) and a strict deterministic-code-vs-AI split: state, dedup, persistence, retries, coverage and final status are always code; AI is only invoked for well-scoped, schema-validated work units (query expansion, page extraction, relevance/fit, ambiguity resolution).

The spec itself defines an MVP (Appendix B) that proves the full pipeline end-to-end with narrowed scope, followed by an additive V1 (Appendix A) that never requires re-architecting the core boundaries. This plan sequences the build from empty repo through MVP, then sketches the V1 additions, so each phase only depends on previously-completed, stable work — nothing gets built against a stub that later forces rework.

**Decisions locked in for this plan** (resolved with the user):
- Canonical data files (`tech_companies_master.xlsx`, `job_applications_master.xlsx`, skills profile, keywords file) live in an **external, gitignored data directory**, path supplied via config/env var. The repo ships only small synthetic fixtures for tests.
- Task 2's MVP scope is **narrowed to ATS + curated directly-crawlable sources** (Greenhouse, Lever, Comeet, Generic Careers Page) — no raw Google/Indeed/Glassdoor/LinkedIn scraping and no SERP API in MVP. That breadth is explicitly deferred to V1.

---

## Phase 0 — Repo Bootstrap

Scaffold `backend/` (FastAPI, `pyproject.toml`, `pytest`), `frontend/` (React+TS+Vite via `npm create vite@latest`), `config/`, `.gitignore` (SQLite file, `node_modules`, Playwright cache, `.env`, the external data dir), and a root `README.md` with run instructions. Add a `DATA_DIR`-style config/env var pointing at the external canonical-files directory.

**Verify**: `uvicorn` boots a FastAPI app with a `GET /health`; `npm run dev` serves a blank Vite+React page; `pytest` runs cleanly with zero tests.

## Phase 1 — Central Data Model & Storage

Define once, shared by everything downstream: `Job`, `Run`, `ApplicationStatus`, `Coverage`, `JobAnalysis`, `Company`, `RoleFamily`, `SearchKeyword`, `SearchSource`. SQLite schema + a **centralized data-access layer** (plain `sqlite3`/lightweight — no generic ORM/Repository framework, per Appendix A.11's explicit deferral).

**Files**: `backend/storage/models.py`, `backend/storage/db.py`, `backend/storage/repository.py`.

**Verify**: unit tests round-trip `Job`/`Run`/`Company` through SQLite; fresh `db.init()` creates all tables.

## Phase 2 — Config & Canonical Data Loader

Loader/validator for Companies, Search Keywords, Role Families, Search Sources (must be data, not hardcoded — Appendix A.14), plus readers for the external canonical files (`job_applications_master.xlsx`, skills profile md) via openpyxl/pandas, pointed at `DATA_DIR`. Stands up the Discovery Ledger persistence shape (`first_found`/`verified`/`task`/`status`, §9).

**Files**: `backend/storage/excel_io.py` (path-configurable via `DATA_DIR`), `backend/coverage/ledger.py`, `config/companies.seed.json`, `config/role_families.json`, `config/search_keywords.json`, `config/search_sources.json` (seed data — real keyword/role-family content to be confirmed against the user's actual `job_search_keywords.md` when available).

**Verify**: seed config loads into SQLite and reads back; a synthetic fixture `job_applications_master.xlsx` round-trips; malformed config is rejected with a clear error.

## Phase 3 — Normalization + Dedup Engine

Pure deterministic, no AI/network dependency: company/title/location/URL/ID normalization, `role_key` (Job/Requisition ID first, else normalized company+title+location+canonical URL, §3), mirror/parallel-posting merge, "URL-only change ≠ new job," "re-report only on material status change."

**Files**: `backend/dedup/normalize.py`, `backend/dedup/role_key.py`, `backend/dedup/engine.py`.

**Verify**: unit tests matching the spec's regression list (§12) — same job via two sources merges to one entity; multiple distinct jobs at one company stay separate; URL-only change is not a new job; status change flags re-report.

## Phase 4 — Application Gate (code path; AI hook stubbed)

Cross-check against `job_applications_master.xlsx` by Job/Requisition ID and company+title variation; set 🔵 with the fixed text "אין פעולה — לא להגיש שוב" on match. AI-ambiguity fallback is a stubbed interface here, wired to real AI in Phase 5. Gmail fallback verification is **deferred past MVP** (not in Appendix B.4's success criteria; needs OAuth/credentials setup not specified in the free stack).

**Files**: `backend/applications/gate.py`, `backend/applications/ambiguity_stub.py`.

**Verify**: unit tests — exact ID match → 🔵; company+title-variation match → 🔵; no match → unflagged; ambiguous case routes to the stub resolver rather than guessing.

## Phase 5 — AIProvider Abstraction, Schemas, Prompts

Swappable `AIProvider` interface, a `FakeProvider` test double, the real `OllamaProvider`, and Pydantic schemas (with `evidence`/`confidence`) for the four AI work units from §10: Query Expansion, Job Extractor/Interpreter, Relevance & Fit, Ambiguity Resolver. Prompts live in external files, not inline strings (Appendix A.10).

**Files**: `backend/ai/provider.py`, `backend/ai/ollama_provider.py`, `backend/ai/fake_provider.py`, `backend/ai/schemas.py`, `backend/ai/prompts/*.md`.

**Verify**: contract tests reject malformed/incomplete AI JSON; `FakeProvider` exercises all four work-unit shapes so Phases 6–8 can be tested without a running Ollama; one manual smoke call to a real local Ollama model confirms a schema-valid extraction response. (Model choice — e.g. a 7–8B class Qwen/Llama/Mistral model — should be picked based on the actual dev machine's RAM/GPU at this point.)

## Phase 6 — Search/Fetch Engine + ATS Adapters (MVP-narrowed)

Web/ATS Fetcher (Playwright + httpx + BeautifulSoup/lxml: pagination, rate limits) plus **only** the MVP adapter set: Greenhouse, Lever, Comeet, Generic Careers Page (per the locked-in decision — no Google/Indeed/Glassdoor/LinkedIn scraping in MVP). Wires in Phase 5's AI Extractor (page → structured job fields) and Query Builder (code-generated keyword combinations + AI semantic variations).

**Files**: `backend/search/fetcher.py`, `backend/search/query_builder.py`, `backend/ats/{base,greenhouse,lever,comeet,generic}.py`, fixture pages under `backend/tests/fixtures/ats_pages/`.

**Verify**: fixture tests per adapter using saved HTML + `FakeProvider`; one live manual smoke run against a real Greenhouse-hosted careers page confirming pagination + real-Ollama extraction.

## Phase 7 — Coverage, Retry State, Discovery Ledger (MVP-basic)

Basic Coverage Checklist and Retry Manager scoped to MVP (units planned/processed, jobs found, duplicates, already-applied, errors — Appendix B.1). State persisted per company/source/page so partial failure doesn't erase progress. Full "5 targeted retries" continuation logic is V1, not MVP (Appendix B.3).

**Files**: `backend/coverage/tracker.py`, `backend/coverage/retry.py` (basic), `backend/coverage/ledger.py` (extended from Phase 2).

**Verify**: unit test simulates source B failing mid-run after source A succeeds; source A's jobs persist and B's failure is recorded without corrupting A's data.

## Phase 8 — Task Orchestrators (Task 1 & Task 2)

Thin orchestrators only, per Appendix A.12 — no duplicated logic, just calling Phases 2–7 in the documented flow (§11: Load Canonical Data → Build Work Units → Search/Fetch → AI Extract → Normalize & Dedup → Application Gate → AI Relevance/Fit → Persist Ledger & Coverage). Task 1 adds the Company Batch Manager (≤150-company segments, frozen at run start, wrap-around rotation, §4). Task 2 adds the role-family × source-family matrix walk (narrowed to MVP sources) with new-company-triggers-full-sweep behavior (§5).

**Files**: `backend/tasks/task1.py`, `backend/tasks/task2.py`, `backend/tasks/batch_manager.py`, `backend/tasks/run_context.py`.

**Verify**: standalone unit test for `batch_manager` rotation/wrap-around/new-company-mid-list; integration test running Task 1 end-to-end against `FakeProvider` + fixtures, asserting a completed `Run` with expected job/dedup/coverage counts.

## Phase 9 — FastAPI Layer

Endpoints scoped to MVP: `POST /api/runs/task1`, `POST /api/runs/task2`, `GET /api/runs/{run_id}`, `GET /api/jobs`, `GET /api/jobs/{job_id}`, `GET /api/dashboard`. `POST /api/jobs/{job_id}/deep-verify` and `GET /api/companies` exist as stubs so the frontend doesn't need rework once V1 fills them in. Runs execute via FastAPI `BackgroundTasks` (no task-queue over-build for MVP scale).

**Files**: `backend/api/routers/{runs,jobs,dashboard}.py`, `backend/api/dto.py`, `backend/api/main.py`.

**Verify**: `TestClient` end-to-end — `POST /api/runs/task1` → poll `GET /api/runs/{run_id}` to completion → `GET /api/jobs` returns persisted jobs.

## Phase 10 — Frontend MVP

The three MVP screens (Appendix B.2): Dashboard (run buttons, last run status, summary metrics), Jobs (status/company/title/fit/location/applied/source link), Run Details (progress/coverage/duplicates/already-applied/errors). TanStack Query + React Router + MUI or shadcn/ui, per Appendix A.6. No Configuration screen yet.

**Files**: `frontend/src/pages/{Dashboard,Jobs,RunDetails}.tsx`, `frontend/src/api/client.ts` (React's only contact point with the backend — never talks to job sites/Excel/AI directly), `frontend/src/types/`.

**Verify**: manual click-through — trigger a run, watch it complete, inspect Run Details and Jobs list with working source links.

## Phase 11 — MVP Integration Pass & Acceptance

Swap fixtures/`FakeProvider` for the real Ollama model and real MVP-scope target sites; walk Appendix B.4's success criteria literally:
- Task 1 & Task 2 runnable from UI with a Run ID/status to completion.
- Jobs from supported sources land in the unified model and persist.
- Same job via >1 source is not shown as duplicate.
- Already-applied job identified and marked 🔵.
- AI relevance/fit output is schema-valid.
- A source failure doesn't erase other sources' results; error shows in Run Details.
- Changing company list/keywords (via config/DB) requires no engine code change.

Also implement the daily smoke test from §12 (source files accessible, batch selected, ≥1 search source works, ledger readable/writable) as an automated check.

**Files**: `backend/tests/smoke_test.py`, `backend/tests/integration/`.

---

## Post-MVP — V1 (additive, no architectural rework per Appendix B.6)

1. **Configuration UI** — Add/Edit screens for Companies, Search Keywords, Role Families, Search Sources over Phase 2's tables; fill in `GET/POST /api/companies` etc.
2. **Scheduler** — APScheduler wrapping the same `task1.py`/`task2.py` orchestrators, independent of UI (cross-platform in-process choice, appropriate given local dev on macOS).
3. **Broader source/ATS coverage** — Workday adapter, Indeed/Glassdoor/Israeli boards/public LinkedIn, layered onto `backend/search/`/`backend/ats/`; only split a real Adapter where there's a genuine technical difference (no generic plugin framework).
4. **Deep Verification pipeline** — Official Job → Apply Path → Live Form Check → Contacts → Final status, on top of existing AI schemas/job model; wires up `POST /api/jobs/{job_id}/deep-verify` for real; consumes the LinkedIn company directory xlsx.
5. **Advanced Retry/Continuation** — extends Phase 7 with the "5 targeted retries per missing component" rule and continuation-run reporting.
6. **Full Deep Verification report generator** — exact §8 field order (status circle, location|work model, Requisition ID, fit%, why-fits, gaps, prior application, LinkedIn connections, textual status, recommendation, apply link).
7. **Gmail fallback for Application Gate**, and optionally `OpenAIProvider` as a second `AIProvider` (no Task/UI changes needed, validating Phase 5's abstraction).

---

## Open Items Still Worth Confirming During Build

- Exact content of `job_search_keywords.md` (real keyword/role-family lists) — seed config in Phase 2 with spec-derived role families as a starting point until the real file is available.
- Concrete Ollama model choice — pick once actual dev-machine specs are known, at Phase 5.
- "Central Israel" location-matching list (Tel Aviv, Gush Dan, etc.) — keep as a small deterministic config list consumed by Normalization (Phase 3), not an AI judgment call.
