# Cognitive AI Learning Platform

Course-first web platform for Artificial Intelligence Introduction and Brain & Cognitive Science Introduction.

## MVP

- Vue + Flask lightweight LMS.
- Seeded demo courses.
- MiroFish-style knowledge graph exploration.
- Cited AI tutor.
- Teacher upload, review, and publish workflow.

## Setup

Backend:

```bash
cd backend
uv sync
uv run python run.py
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

## Tests

```bash
cd backend && uv run pytest -q
cd frontend && npm test && npm run build
```

## Notes

The graph interaction model is inspired by MiroFish GraphPanel. EDUFISH/MiroFish code is treated as reference unless a later implementation decision explicitly imports compatible code.
