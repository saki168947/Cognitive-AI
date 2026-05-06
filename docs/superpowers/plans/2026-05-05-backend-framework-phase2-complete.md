# Backend Framework — Phase 2 Complete

> Date: 2026-05-05
> Status: 108 tests passing

## Backend Architecture (Final State)

```
backend/app/
├── __init__.py              # Flask app factory
├── config.py                # Config (LLM, embedding, paths)
├── db.py                    # SQLAlchemy instance
├── migrations.py            # Lightweight ALTER-TABLE migrations for SQLite
├── models.py                # All ORM models
├── llm_client.py            # OpenAI-compatible LLM wrapper (chat/json/stream)
│
├── rag/                     # === Phase 1: RAG infrastructure ===
│   ├── extractor.py         #   pypdf + text file extraction (was: broken UTF-8 decode)
│   ├── chunker.py           #   Smart semantic chunking (CN headers, MD, length-aware)
│   ├── embedding.py         #   OpenAI-compatible embeddings client
│   └── vector_store.py      #   ChromaDB wrapper (zero-config)
│
├── agents/                  # === Phase 2: Agent framework ===
│   ├── registry.py          #   Tool registry with self-registration decorator
│   ├── base.py              #   Agent class with tool-calling loop + SSE events
│   ├── definitions.py       #   3 specialized agents (tutor, document-analyst, graph-explorer)
│   └── tools/
│       └── course_tools.py  #   5 built-in tools: search_materials, search_concept_graph, ...
│
├── services/                # Business logic
│   ├── course_service.py
│   ├── activity_service.py
│   ├── material_service.py  #   Rewritten: real extraction + chunking + embedding + LLM concept extraction
│   ├── tutor_service.py     #   Rewritten: RAG pipeline with graceful fallback to keyword
│   ├── review_service.py
│   ├── seed_data.py
│   ├── user_service.py      #   NEW: lightweight user CRUD
│   ├── assignment_service.py # NEW: teacher assigns work, students submit, teachers grade
│   ├── progress_service.py  #   NEW: event-based progress tracking + cohort aggregation
│   ├── job_queue.py         #   NEW: thread-pool background job queue
│   └── job_handlers.py      #   NEW: ingest_material handler (extract + embed + LLM async)
│
├── api/                     # HTTP layer
│   ├── courses.py           # Existing
│   ├── activities.py        # Existing
│   ├── graph.py             # Existing
│   ├── materials.py         # Updated: ?async=1 returns job_id
│   ├── review.py            # Existing
│   ├── tutor.py             # Updated: ?stream=1 SSE
│   ├── agents.py            # NEW: list/run/stream agents
│   ├── users.py             # NEW
│   ├── assignments.py       # NEW
│   ├── progress.py          # NEW
│   └── jobs.py              # NEW: job status polling
│
└── tests/                   # 108 tests
    ├── test_courses_api.py
    ├── test_activities_api.py
    ├── test_graph_api.py
    ├── test_materials_api.py
    ├── test_review_publish.py
    ├── test_seed_data.py
    ├── test_tutor_service.py
    ├── test_rag_modules.py            # NEW: 10 tests
    ├── test_user_assignment_progress.py  # NEW: 9 tests
    ├── test_agents.py                 # NEW: 12 tests
    └── test_api_extended.py           # NEW: 10 tests
```

## What's New in Phase 2

### 1. Agent Framework

A tool-calling agent system that mirrors the patterns from PathMind-AI/hermes-agent.

**Tool registry**: tools self-register via `@register_tool` decorator. Each tool has a name, description, JSONSchema for parameters, and a handler. The registry exposes `schemas_for(names)` to build OpenAI tool schemas for a specific agent.

**Built-in tools** (all registered, all backed by real DB queries):
- `search_materials` — semantic search via vector store (returns empty if no embedding API key)
- `search_concept_graph` — query Concept and GraphEdge tables
- `get_chapter` — retrieve full chapter content
- `list_chapters` — list course chapters
- `get_quiz_items_for_chapter` — get quiz items

**Specialized agents** (in `definitions.py`):
- `tutor` — student-facing Q&A, has 5 tools, temp 0.7
- `document-analyst` — extracts concepts/edges/quiz from materials, has 2 tools, temp 0.3, JSON output
- `graph-explorer` — knowledge graph navigation, has 3 tools, temp 0.5

**Agent loop** (`base.py` → `Agent._iterate`):
1. Build messages from system prompt + context + user input
2. Call LLM with tool schemas
3. If tool calls returned: execute each, append results to messages, loop
4. If text response: emit `answer` event and stop
5. Cap at `max_iterations` (default 8) to prevent runaway loops

**Streaming**: `Agent.stream()` yields `AgentEvent` objects (`thinking | tool_call | tool_result | answer | error`) that serialize to SSE format.

### 2. User / Assignment / Submission Models

The platform now has the noun-set a real teaching platform needs:

- `User` — students and teachers (no auth yet, just identity)
- `Assignment` — teacher-created work, with course_id, optional chapter/activity link, type, due_at, status (draft/published/archived)
- `Submission` — student response to an assignment, with status (submitted/graded), score, feedback
- `ProgressEvent` — append-only event log of student actions (viewed, started, completed, answered_quiz, asked_tutor, etc.)

This unblocks the "老师布置/分析、学生提交" closed loop that was missing.

### 3. Progress Aggregation

`ProgressService.summary_for_student(id)` returns counts by event type, completed chapters/activities, recent events.
`ProgressService.cohort_summary(course_id)` aggregates across students for the teacher dashboard.

### 4. Background Job Queue

A `ThreadPoolExecutor`-backed queue with state persisted in the `Job` table. Material upload can now run in async mode (`?async=1`) — file is saved synchronously, then heavy work (extraction → embedding → LLM concept extraction) runs in background. Frontend polls `/api/jobs/<id>` for status.

This matters because LLM calls can take 10–30s; we don't want the upload request to block.

### 5. Database Migrations

`app/migrations.py` runs at startup and adds missing columns via `ALTER TABLE` for old SQLite databases. New tables are handled automatically by `db.create_all()`. So upgrading from Phase 1 to Phase 2 doesn't require dropping the database.

## API Surface (New Endpoints)

```
# Users
GET    /api/users[?role=student|teacher]
POST   /api/users                        {name, email?, role}
GET    /api/users/<id>

# Assignments
GET    /api/assignments[?course_id=&status=]
POST   /api/assignments                  {course_id, title, assignment_type, ...}
GET    /api/assignments/<id>
POST   /api/assignments/<id>/publish
POST   /api/assignments/<id>/archive

# Submissions
GET    /api/assignments/<id>/submissions
POST   /api/assignments/<id>/submissions {student_id, content}
POST   /api/submissions/<id>/grade       {score, feedback}
GET    /api/students/<id>/submissions

# Progress
POST   /api/progress/events              {student_id, event_type, course_id?, chapter_id?, ...}
GET    /api/progress/students/<id>
GET    /api/progress/courses/<id>

# Agents
GET    /api/agents
POST   /api/agents/<name>/run            {input, context?}
POST   /api/agents/<name>/stream         {input, context?}        (SSE)

# Jobs
GET    /api/jobs/<id>

# Materials (async option)
POST   /api/materials/upload?async=1     → returns {material, job_id}
```

## Design Decisions

### Why thread pool, not Celery?
For a teaching platform with two courses and dozens of materials, a 2-worker thread pool is enough. Adding Celery means Redis, broker config, worker process management — overkill. Easy to swap later if scale demands.

### Why ChromaDB, not pgvector?
- Zero external deps (SQLite-backed, no server)
- Persists to `instance/chromadb/`
- pgvector requires PostgreSQL; we're on SQLite
- Easy migration path: same query API as PathMind-AI's pgvector code

### Why no auth?
Auth is a layer above this, and forcing a specific provider here would constrain deployment. The User table provides identity; a real deployment would add a JWT middleware in front (or trust an upstream proxy).

### Why event-based progress, not status flags?
- Append-only is simpler to reason about
- Can recompute summaries from events at any time
- Supports analytics (cohort heatmaps, retention curves) without schema changes

## Test Coverage

```
test_courses_api.py             7 tests
test_activities_api.py         17 tests
test_graph_api.py               3 tests
test_materials_api.py           7 tests
test_review_publish.py         17 tests
test_seed_data.py               9 tests
test_tutor_service.py           7 tests
test_rag_modules.py            10 tests   ← Phase 1
test_user_assignment_progress.py  9 tests ← Phase 2
test_agents.py                 12 tests   ← Phase 2
test_api_extended.py           10 tests   ← Phase 2
─────────────────────────────────────────
Total                         108 tests passing
```

## What's Still Stubbed (Honest Audit)

| Component | Status | Notes |
|-----------|--------|-------|
| LLM concept extraction | Code complete, untested with real LLM | Need API key to verify quality |
| AI Tutor RAG | Code complete, untested with real LLM | Need API key + uploaded materials |
| Agent tool-calling loop | Code complete, untested with real LLM | Same |
| Background jobs | Code complete, partially tested | Async upload test verifies enqueue, not full execution |
| Auth | Not implemented | Intentional — add at deployment |
| Cognitive experiments (jsPsych) | Not started | Phase 3 |
| Code labs (JupyterLite) | Not started | Phase 3 |
| Simulation (MiroFish-style) | Not started | Phase 3 |

## Next Steps

1. **Configure `.env`** with LLM_API_KEY + EMBEDDING_API_KEY
2. **Smoke test** the agent endpoints with real credentials (run document-analyst on a real PDF)
3. **Frontend integration** — Tutor streaming UI, async upload progress, assignment dashboards
4. **Phase 3** — experiments and simulation
