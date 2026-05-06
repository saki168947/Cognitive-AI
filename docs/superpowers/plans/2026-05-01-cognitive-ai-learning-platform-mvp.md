# Cognitive AI Learning Platform MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first working vertical slice of the course-first cognitive AI learning platform: seeded courses, chapter learning, MiroFish-style graph exploration, cited AI tutor, and teacher review/publish flow.

**Architecture:** Start from an empty repository and scaffold a Vue 3 + Flask app. Keep the backend service-oriented: course data, graph data, review workflow, material ingestion, and tutor/RAG each have focused modules. Implement MVP storage with SQLite and local files, with interfaces that can later move to Postgres, object storage, and a stronger vector database.

**Tech Stack:** Vue 3, Vite, Pinia, Vue Router, D3, Flask, SQLAlchemy, SQLite, pytest, Vitest, OpenAI-compatible LLM API.

---

## Scope Notes

This plan intentionally builds a vertical MVP rather than the full future platform. It includes:

- Seeded "人工智能导论" and "脑与认知科学导论" courses.
- Student course/chapter workspace.
- Teacher Studio upload/review/publish loop.
- Knowledge graph viewer based on MiroFish GraphPanel interaction patterns.
- Cited AI tutor using published chunks and graph neighbors.

It excludes:

- Full LMS enrollment, gradebook, attendance, certificates, SSO, payment, and marketplace.
- Adaptive recommendations.
- Required MiroFish multi-agent simulation.
- Full Moodle/Open edX/Frappe integration.

Because the current directory is not a git repository, Task 0 initializes git so later plan steps can make frequent commits.

## File Structure

Create this structure:

```text
.
├── README.md
├── .gitignore
├── .env.example
├── package.json
├── backend/
│   ├── pyproject.toml
│   ├── run.py
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── db.py
│   │   ├── models.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── courses.py
│   │   │   ├── graph.py
│   │   │   ├── review.py
│   │   │   ├── tutor.py
│   │   │   └── materials.py
│   │   ├── services/
│   │   │   ├── seed_data.py
│   │   │   ├── course_service.py
│   │   │   ├── review_service.py
│   │   │   ├── material_service.py
│   │   │   └── tutor_service.py
│   │   └── tests/
│   │       ├── conftest.py
│   │       ├── test_seed_data.py
│   │       ├── test_courses_api.py
│   │       ├── test_graph_api.py
│   │       ├── test_review_publish.py
│   │       └── test_tutor_service.py
│   └── uploads/
└── frontend/
    ├── index.html
    ├── package.json
    ├── vite.config.js
    ├── src/
    │   ├── main.js
    │   ├── App.vue
    │   ├── router/index.js
    │   ├── api/client.js
    │   ├── api/courses.js
    │   ├── api/graph.js
    │   ├── api/review.js
    │   ├── api/tutor.js
    │   ├── views/DashboardView.vue
    │   ├── views/CourseView.vue
    │   ├── views/TeacherStudioView.vue
    │   ├── components/GraphPanel.vue
    │   ├── components/AITutorPanel.vue
    │   ├── components/ChapterWorkspace.vue
    │   ├── components/ReviewQueue.vue
    │   └── styles/app.css
    └── tests/
        └── unit/graphTransform.test.js
```

---

### Task 0: Repository And Tooling Baseline

**Files:**
- Create: `.gitignore`
- Create: `README.md`
- Create: `.env.example`
- Create: `package.json`

- [ ] **Step 1: Initialize git**

Run:

```bash
git init
```

Expected: repository initialized in the current directory.

- [ ] **Step 2: Create root metadata files**

Create `.gitignore`:

```gitignore
.env
.venv/
__pycache__/
.pytest_cache/
node_modules/
dist/
backend/uploads/*
!backend/uploads/.gitkeep
backend/instance/
*.sqlite
.superpowers/
```

Create `.env.example`:

```env
FLASK_ENV=development
DATABASE_URL=sqlite:///app.sqlite
UPLOAD_DIR=uploads
LLM_API_KEY=
LLM_BASE_URL=
LLM_MODEL_NAME=
```

Create root `package.json`:

```json
{
  "name": "cognitive-ai-learning-platform",
  "private": true,
  "version": "0.1.0",
  "scripts": {
    "setup": "npm install && if [ -d frontend ]; then cd frontend && npm install; else echo 'frontend not scaffolded yet'; fi",
    "dev": "if [ -d backend ] && [ -d frontend ]; then concurrently --kill-others -n backend,frontend -c green,cyan \"cd backend && uv run python run.py\" \"cd frontend && npm run dev\"; else echo 'backend/frontend not scaffolded yet'; exit 1; fi",
    "test": "npm run test:backend && npm run test:frontend",
    "test:backend": "if [ -d backend ]; then cd backend && uv run pytest; else echo 'backend not scaffolded yet'; fi",
    "test:frontend": "if [ -d frontend ]; then cd frontend && npm test; else echo 'frontend not scaffolded yet'; fi",
    "build": "if [ -d frontend ]; then cd frontend && npm run build; else echo 'frontend not scaffolded yet'; fi"
  },
  "devDependencies": {
    "concurrently": "^9.2.1"
  }
}
```

Create `README.md`:

```markdown
# Cognitive AI Learning Platform

Course-first web platform for Artificial Intelligence Introduction and Brain & Cognitive Science Introduction.

## MVP

- Vue + Flask lightweight LMS.
- Seeded demo courses.
- MiroFish-style knowledge graph exploration.
- Cited AI tutor.
- Teacher upload, review, and publish workflow.
```

- [ ] **Step 3: Commit baseline**

Run:

```bash
git add .gitignore README.md .env.example package.json
git commit -m "chore: initialize project baseline"
```

Expected: commit succeeds.

---

### Task 1: Flask Backend Skeleton

**Files:**
- Create: `backend/pyproject.toml`
- Create: `backend/run.py`
- Create: `backend/app/__init__.py`
- Create: `backend/app/config.py`
- Create: `backend/app/db.py`
- Create: `backend/app/api/__init__.py`
- Create: `backend/app/tests/conftest.py`

- [ ] **Step 1: Create backend package config**

Create `backend/pyproject.toml`:

```toml
[project]
name = "cognitive-ai-learning-platform-backend"
version = "0.1.0"
requires-python = ">=3.11,<3.13"
dependencies = [
  "flask>=3.0.0",
  "flask-cors>=6.0.0",
  "flask-sqlalchemy>=3.1.1",
  "python-dotenv>=1.0.0",
  "openai>=1.0.0",
  "pypdf>=4.0.0"
]

[dependency-groups]
dev = [
  "pytest>=8.0.0",
  "pytest-cov>=5.0.0"
]
```

- [ ] **Step 2: Create app factory**

Create `backend/app/config.py`:

```python
import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///app.sqlite")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
    LLM_API_KEY = os.getenv("LLM_API_KEY", "")
    LLM_BASE_URL = os.getenv("LLM_BASE_URL", "")
    LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "")
```

Create `backend/app/db.py`:

```python
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
```

Create `backend/app/api/__init__.py`:

```python
from flask import Blueprint

api_bp = Blueprint("api", __name__, url_prefix="/api")
```

Create `backend/app/__init__.py`:

```python
import os

from flask import Flask, jsonify
from flask_cors import CORS

from .config import Config
from .db import db
from .api import api_bp


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    CORS(app)
    db.init_app(app)
    app.register_blueprint(api_bp)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    os.makedirs(app.instance_path, exist_ok=True)
    try:
        from . import models  # noqa: F401
    except ImportError:
        pass

    with app.app_context():
        db.create_all()

    return app
```

Create `backend/run.py`:

```python
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
```

- [ ] **Step 3: Write backend test fixture**

Create `backend/app/tests/conftest.py`:

```python
import pytest

from app import create_app
from app.db import db


@pytest.fixture()
def app():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "UPLOAD_DIR": "/tmp/cognitive-ai-learning-platform-test-uploads",
    })
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app


@pytest.fixture()
def client(app):
    return app.test_client()
```

- [ ] **Step 4: Verify backend skeleton**

Run:

```bash
cd backend && uv sync && uv run pytest -q
```

Expected: pytest exits successfully with no tests collected or with fixture import succeeding.

- [ ] **Step 5: Commit**

Run:

```bash
git add backend
git commit -m "chore: scaffold flask backend"
```

Expected: commit succeeds.

---

### Task 2: Core Models And Seed Courses

**Files:**
- Create: `backend/app/models.py`
- Create: `backend/app/services/seed_data.py`
- Create: `backend/app/services/course_service.py`
- Create: `backend/app/tests/test_seed_data.py`

- [ ] **Step 1: Write seed data test**

Create `backend/app/tests/test_seed_data.py`:

```python
from app.db import db
from app.models import Concept, Course, GraphEdge
from app.services.seed_data import seed_courses
from app.services.course_service import CourseService


def test_seed_courses_create_two_courses(app):
    seed_courses()

    courses = CourseService.list_courses()

    assert len(courses) == 2
    titles = {course.title for course in courses}
    assert "人工智能导论" in titles
    assert "脑与认知科学导论" in titles


def test_seed_courses_are_idempotent(app):
    seed_courses()
    seed_courses()

    graph = CourseService.get_graph()

    assert Course.query.count() == 2
    assert len(graph["nodes"]) == 5
    assert len({node["id"] for node in graph["nodes"]}) == 5
    assert len(graph["edges"]) == 3
    assert len({edge["id"] for edge in graph["edges"]}) == 3
    assert Concept.query.count() == len(graph["nodes"])
    assert GraphEdge.query.count() == len(graph["edges"])


def test_seed_courses_preserve_user_authored_content(app):
    seed_courses()
    db.session.add(Course(id="custom-course", title="教师自建课程", summary=""))
    db.session.add(
        Concept(
            id="concept-custom",
            course_id="custom-course",
            label="Custom Concept",
            definition="Teacher authored content.",
        )
    )
    db.session.commit()

    seed_courses()

    assert db.session.get(Course, "custom-course") is not None
    assert db.session.get(Concept, "concept-custom") is not None


def test_seed_courses_include_cross_course_concepts(app):
    seed_courses()

    graph = CourseService.get_graph()
    labels = {node["label"] for node in graph["nodes"]}
    relationships = {edge["relationship"] for edge in graph["edges"]}

    assert "Transformer Attention" in labels
    assert "Human Attention" in labels
    assert "RELATED_TO" in relationships


def test_ai_intro_graph_includes_connected_cross_course_concepts(app):
    seed_courses()

    graph = CourseService.get_graph("ai-intro")
    labels = {node["label"] for node in graph["nodes"]}

    assert "Transformer Attention" in labels
    assert "Human Attention" in labels
    assert "Reward System" in labels


def test_brain_cog_intro_graph_includes_human_attention(app):
    seed_courses()

    graph = CourseService.get_graph("brain-cog-intro")
    labels = {node["label"] for node in graph["nodes"]}

    assert "Human Attention" in labels
    assert "Heuristic Search" not in labels
    assert "Transformer Attention" not in labels


def test_course_graph_skips_edges_with_missing_endpoints(app):
    seed_courses()
    db.session.add(
        GraphEdge(
            id="edge-dangling",
            course_id="ai-intro",
            source_id="concept-search",
            target_id="concept-missing",
            relationship="RELATED_TO",
            evidence="Invalid graph draft.",
        )
    )
    db.session.commit()

    graph = CourseService.get_graph("ai-intro")
    edge_ids = {edge["id"] for edge in graph["edges"]}

    assert "edge-dangling" not in edge_ids


def test_course_graph_skips_edges_with_unpublished_endpoints(app):
    seed_courses()
    human_attention = db.session.get(Concept, "concept-human-attention")
    human_attention.status = "draft"
    db.session.commit()

    graph = CourseService.get_graph("ai-intro")
    edge_ids = {edge["id"] for edge in graph["edges"]}
    node_ids = {node["id"] for node in graph["nodes"]}

    assert "edge-attention-related" not in edge_ids
    assert "concept-human-attention" not in node_ids
```

- [ ] **Step 2: Run failing test**

Run:

```bash
cd backend && uv run pytest app/tests/test_seed_data.py -q
```

Expected: FAIL because models and services do not exist.

- [ ] **Step 3: Implement models**

Create `backend/app/models.py`:

```python
from datetime import datetime, timezone

from .db import db


def utc_now():
    return datetime.now(timezone.utc)


class Course(db.Model):
    id = db.Column(db.String, primary_key=True)
    title = db.Column(db.String, nullable=False)
    summary = db.Column(db.Text, nullable=False, default="")
    status = db.Column(db.String, nullable=False, default="published")
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)


class Chapter(db.Model):
    id = db.Column(db.String, primary_key=True)
    course_id = db.Column(db.String, db.ForeignKey("course.id"), nullable=False)
    order = db.Column(db.Integer, nullable=False, default=0)
    title = db.Column(db.String, nullable=False)
    objectives = db.Column(db.Text, nullable=False, default="")
    body = db.Column(db.Text, nullable=False, default="")
    course = db.relationship("Course", backref=db.backref("chapters", lazy=True))


class Concept(db.Model):
    id = db.Column(db.String, primary_key=True)
    course_id = db.Column(db.String, db.ForeignKey("course.id"), nullable=False)
    label = db.Column(db.String, nullable=False)
    definition = db.Column(db.Text, nullable=False, default="")
    status = db.Column(db.String, nullable=False, default="published")


class GraphEdge(db.Model):
    id = db.Column(db.String, primary_key=True)
    course_id = db.Column(db.String, db.ForeignKey("course.id"), nullable=False)
    source_id = db.Column(db.String, db.ForeignKey("concept.id"), nullable=False)
    target_id = db.Column(db.String, db.ForeignKey("concept.id"), nullable=False)
    relationship = db.Column(db.String, nullable=False)
    status = db.Column(db.String, nullable=False, default="published")
    evidence = db.Column(db.Text, nullable=False, default="")
    source = db.relationship("Concept", foreign_keys=[source_id], backref=db.backref("outgoing_edges", lazy=True))
    target = db.relationship("Concept", foreign_keys=[target_id], backref=db.backref("incoming_edges", lazy=True))


class QuizItem(db.Model):
    id = db.Column(db.String, primary_key=True)
    chapter_id = db.Column(db.String, db.ForeignKey("chapter.id"), nullable=False)
    prompt = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    explanation = db.Column(db.Text, nullable=False, default="")
```

- [ ] **Step 4: Implement seed and course service**

Create `backend/app/services/course_service.py`:

```python
from sqlalchemy import or_
from sqlalchemy.orm import aliased

from app.db import db
from app.models import Chapter, Concept, Course, GraphEdge, QuizItem


class CourseService:
    @staticmethod
    def list_courses():
        return Course.query.order_by(Course.title.asc()).all()

    @staticmethod
    def get_course(course_id):
        return db.session.get(Course, course_id)

    @staticmethod
    def get_course_detail(course_id):
        course = db.get_or_404(Course, course_id)
        chapters = Chapter.query.filter_by(course_id=course_id).order_by(Chapter.order.asc()).all()
        return {
            "id": course.id,
            "title": course.title,
            "summary": course.summary,
            "chapters": [
                {
                    "id": chapter.id,
                    "title": chapter.title,
                    "order": chapter.order,
                    "objectives": chapter.objectives,
                    "body": chapter.body,
                }
                for chapter in chapters
            ],
        }

    @staticmethod
    def get_chapter(chapter_id):
        chapter = db.get_or_404(Chapter, chapter_id)
        quiz_items = QuizItem.query.filter_by(chapter_id=chapter_id).all()
        return {
            "id": chapter.id,
            "course_id": chapter.course_id,
            "title": chapter.title,
            "objectives": chapter.objectives,
            "body": chapter.body,
            "quiz_items": [
                {
                    "id": item.id,
                    "prompt": item.prompt,
                    "answer": item.answer,
                    "explanation": item.explanation,
                }
                for item in quiz_items
            ],
        }

    @staticmethod
    def get_graph(course_id=None):
        SourceConcept = aliased(Concept)
        TargetConcept = aliased(Concept)
        edges_query = (
            db.session.query(GraphEdge)
            .join(SourceConcept, GraphEdge.source_id == SourceConcept.id)
            .join(TargetConcept, GraphEdge.target_id == TargetConcept.id)
            .filter(
                GraphEdge.status == "published",
                SourceConcept.status == "published",
                TargetConcept.status == "published",
            )
        )

        concept_query = Concept.query.filter_by(status="published")
        if course_id:
            edges = edges_query.filter(GraphEdge.course_id == course_id).all()
            connected_ids = set()
            for edge in edges:
                connected_ids.add(edge.source_id)
                connected_ids.add(edge.target_id)
            concepts = Concept.query.filter(
                Concept.status == "published",
                or_(
                    Concept.course_id == course_id,
                    Concept.id.in_(connected_ids),
                ),
            ).all()
        else:
            edges = edges_query.all()
            concepts = concept_query.all()
        nodes = [
            {
                "id": concept.id,
                "label": concept.label,
                "type": "Concept",
                "definition": concept.definition,
            }
            for concept in concepts
        ]
        return {
            "nodes": nodes,
            "edges": [
                {
                    "id": edge.id,
                    "source": edge.source_id,
                    "target": edge.target_id,
                    "relationship": edge.relationship,
                    "evidence": edge.evidence,
                }
                for edge in edges
            ],
        }
```

Create `backend/app/services/seed_data.py`:

```python
from app.db import db
from app.models import Chapter, Concept, Course, GraphEdge, QuizItem


def _merge_all(items):
    for item in items:
        db.session.merge(item)


def seed_courses():
    courses = [
        Course(
            id="ai-intro",
            title="人工智能导论",
            summary="Search, reasoning, machine learning, neural networks, reinforcement learning, language, vision, knowledge graphs, and AI ethics.",
        ),
        Course(
            id="brain-cog-intro",
            title="脑与认知科学导论",
            summary="Neurons, brain systems, attention, memory, language, emotion, consciousness, brain imaging, and cognitive models.",
        ),
    ]
    _merge_all(courses)

    chapters = [
        Chapter(id="ai-search", course_id="ai-intro", order=1, title="Search and Problem Solving", objectives="Understand state spaces, search strategies, and heuristic reasoning.", body="Search frames intelligence as finding paths through structured problem spaces."),
        Chapter(id="ai-learning", course_id="ai-intro", order=2, title="Learning and Neural Networks", objectives="Understand representation learning and neural network basics.", body="Neural networks learn layered representations from data."),
        Chapter(id="brain-attention", course_id="brain-cog-intro", order=1, title="Attention and Cognitive Control", objectives="Understand selective attention, working memory, and executive control.", body="Attention selects information for processing and action."),
        Chapter(id="brain-reward", course_id="brain-cog-intro", order=2, title="Reward and Decision Making", objectives="Understand reward systems and decision behavior.", body="Reward learning connects action, feedback, and future choice."),
    ]
    _merge_all(chapters)

    concepts = [
        Concept(id="concept-search", course_id="ai-intro", label="Heuristic Search", definition="A strategy for using estimates to guide problem solving."),
        Concept(id="concept-transformer-attention", course_id="ai-intro", label="Transformer Attention", definition="A neural mechanism for weighting token relationships in context."),
        Concept(id="concept-human-attention", course_id="brain-cog-intro", label="Human Attention", definition="A cognitive process for selecting information for deeper processing."),
        Concept(id="concept-rl", course_id="ai-intro", label="Reinforcement Learning", definition="Learning actions from rewards and penalties."),
        Concept(id="concept-reward-system", course_id="brain-cog-intro", label="Reward System", definition="Neural systems involved in motivation, valuation, and learning from outcomes."),
    ]
    _merge_all(concepts)

    edges = [
        GraphEdge(id="edge-attention-related", course_id="ai-intro", source_id="concept-transformer-attention", target_id="concept-human-attention", relationship="RELATED_TO", evidence="Both involve selective weighting, but operate in different systems."),
        GraphEdge(id="edge-rl-reward", course_id="ai-intro", source_id="concept-rl", target_id="concept-reward-system", relationship="RELATED_TO", evidence="Reinforcement learning is inspired by reward-driven behavior and decision processes."),
        GraphEdge(id="edge-search-prereq", course_id="ai-intro", source_id="concept-search", target_id="concept-rl", relationship="PREREQUISITE_OF", evidence="Search concepts help explain planning in reinforcement learning."),
    ]
    _merge_all(edges)

    quiz_items = [
        QuizItem(id="quiz-ai-search-1", chapter_id="ai-search", prompt="What is the role of a heuristic in search?", answer="It estimates which states are more promising.", explanation="A heuristic guides search without guaranteeing perfect knowledge."),
        QuizItem(id="quiz-brain-attention-1", chapter_id="brain-attention", prompt="How is human attention different from transformer attention?", answer="Human attention is a biological cognitive process; transformer attention is a computational weighting mechanism.", explanation="They are analogous but not identical."),
    ]
    _merge_all(quiz_items)
    db.session.commit()
```

- [ ] **Step 5: Run seed tests**

Run:

```bash
cd backend && uv run pytest app/tests/test_seed_data.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit**

Run:

```bash
git add backend/app/models.py backend/app/services backend/app/tests/test_seed_data.py
git commit -m "feat: add seeded course graph data"
```

Expected: commit succeeds.

---

### Task 3: Courses And Graph API

**Files:**
- Create: `backend/app/api/courses.py`
- Create: `backend/app/api/graph.py`
- Modify: `backend/app/api/__init__.py`
- Create: `backend/app/tests/test_courses_api.py`
- Create: `backend/app/tests/test_graph_api.py`

- [ ] **Step 1: Write API tests**

Create `backend/app/tests/test_courses_api.py`:

```python
from app.services.seed_data import seed_courses


def test_list_courses_returns_seed_courses(client, app):
    with app.app_context():
        seed_courses()

    res = client.get("/api/courses")
    payload = res.get_json()

    assert res.status_code == 200
    assert payload["success"] is True
    assert len(payload["data"]) == 2


def test_list_courses_auto_seeds_when_empty(client):
    res = client.get("/api/courses")
    payload = res.get_json()

    assert res.status_code == 200
    assert payload["success"] is True
    assert len(payload["data"]) == 2


def test_get_course_detail_includes_chapters(client, app):
    with app.app_context():
        seed_courses()

    res = client.get("/api/courses/ai-intro")
    payload = res.get_json()

    assert res.status_code == 200
    assert payload["data"]["id"] == "ai-intro"
    assert payload["data"]["chapters"][0]["id"] == "ai-search"


def test_get_missing_course_returns_json_error(client):
    res = client.get("/api/courses/missing-course")
    payload = res.get_json()

    assert res.status_code == 404
    assert payload["success"] is False
    assert "not found" in payload["error"].lower()


def test_get_chapter_detail_includes_quiz_items(client, app):
    with app.app_context():
        seed_courses()

    res = client.get("/api/chapters/ai-search")
    payload = res.get_json()

    assert res.status_code == 200
    assert payload["success"] is True
    assert payload["data"]["id"] == "ai-search"
    assert payload["data"]["quiz_items"][0]["id"] == "quiz-ai-search-1"


def test_get_missing_chapter_returns_json_error(client):
    res = client.get("/api/chapters/missing-chapter")
    payload = res.get_json()

    assert res.status_code == 404
    assert payload["success"] is False
    assert "not found" in payload["error"].lower()
```

Create `backend/app/tests/test_graph_api.py`:

```python
from app.services.seed_data import seed_courses


def test_graph_endpoint_returns_nodes_and_edges(client, app):
    with app.app_context():
        seed_courses()

    res = client.get("/api/graph")
    payload = res.get_json()

    assert res.status_code == 200
    assert payload["success"] is True
    assert any(node["label"] == "Transformer Attention" for node in payload["data"]["nodes"])
    assert any(edge["relationship"] == "RELATED_TO" for edge in payload["data"]["edges"])


def test_graph_endpoint_auto_seeds_when_empty(client):
    res = client.get("/api/graph")
    payload = res.get_json()

    assert res.status_code == 200
    assert payload["success"] is True
    assert any(node["label"] == "Transformer Attention" for node in payload["data"]["nodes"])
    assert any(edge["relationship"] == "RELATED_TO" for edge in payload["data"]["edges"])


def test_graph_endpoint_scopes_nodes_by_course(client, app):
    with app.app_context():
        seed_courses()

    res = client.get("/api/graph?course_id=brain-cog-intro")
    payload = res.get_json()
    labels = {node["label"] for node in payload["data"]["nodes"]}

    assert res.status_code == 200
    assert "Human Attention" in labels
    assert "Heuristic Search" not in labels
```

- [ ] **Step 2: Run failing API tests**

Run:

```bash
cd backend && uv run pytest app/tests/test_courses_api.py app/tests/test_graph_api.py -q
```

Expected: FAIL because routes are not registered.

- [ ] **Step 3: Implement routes**

Create `backend/app/api/courses.py`:

```python
from flask import jsonify

from app.api import api_bp
from app.services.course_service import CourseService
from app.services.seed_data import seed_courses


@api_bp.get("/courses")
def list_courses():
    courses = CourseService.list_courses()
    if not courses:
        seed_courses()
        courses = CourseService.list_courses()
    return jsonify({
        "success": True,
        "data": [
            {"id": course.id, "title": course.title, "summary": course.summary, "status": course.status}
            for course in courses
        ],
    })


@api_bp.get("/courses/<course_id>")
def get_course(course_id):
    return jsonify({"success": True, "data": CourseService.get_course_detail(course_id)})


@api_bp.get("/chapters/<chapter_id>")
def get_chapter(chapter_id):
    return jsonify({"success": True, "data": CourseService.get_chapter(chapter_id)})
```

Create `backend/app/api/graph.py`:

```python
from flask import jsonify, request

from app.api import api_bp
from app.services.course_service import CourseService
from app.services.seed_data import seed_courses


@api_bp.get("/graph")
def get_graph():
    if not CourseService.list_courses():
        seed_courses()
    course_id = request.args.get("course_id")
    return jsonify({"success": True, "data": CourseService.get_graph(course_id=course_id)})
```

Modify `backend/app/api/__init__.py`:

```python
from flask import Blueprint, jsonify
from werkzeug.exceptions import NotFound

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.errorhandler(NotFound)
def handle_not_found(error):
    return jsonify({"success": False, "error": error.description}), 404


from . import courses  # noqa: E402,F401
from . import graph  # noqa: E402,F401
```

- [ ] **Step 4: Run API tests**

Run:

```bash
cd backend && uv run pytest app/tests/test_courses_api.py app/tests/test_graph_api.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

Run:

```bash
git add backend/app/api backend/app/tests/test_courses_api.py backend/app/tests/test_graph_api.py
git commit -m "feat: expose course and graph APIs"
```

Expected: commit succeeds.

---

### Task 4: Teacher Review And Publish Workflow

**Files:**
- Modify: `backend/app/models.py`
- Create: `backend/app/services/review_service.py`
- Create: `backend/app/api/review.py`
- Modify: `backend/app/api/__init__.py`
- Create: `backend/app/tests/test_review_publish.py`

- [ ] **Step 1: Write review workflow test**

Create `backend/app/tests/test_review_publish.py`:

```python
from app.db import db
from app.models import Concept, GraphEdge
from app.services.course_service import CourseService
from app.services.review_service import ReviewService
from app.services.seed_data import seed_courses


def test_review_publish_creates_published_concept_and_edge(app):
    with app.app_context():
        seed_courses()
        item = ReviewService.create_graph_suggestion(
            title="Working Memory cross-link",
            payload={
                "course_id": "brain-cog-intro",
                "concepts": [
                    {"id": "concept-working-memory", "course_id": "brain-cog-intro", "label": "Working Memory", "definition": "Temporary maintenance and manipulation of information."}
                ],
                "edges": [
                    {"id": "edge-working-memory-attention", "course_id": "brain-cog-intro", "source": "concept-working-memory", "target": "concept-human-attention", "relationship": "RELATED_TO", "evidence": "Working memory and attention are tightly coupled."}
                ],
            },
        )

        ReviewService.approve_item(item.id, reviewer="teacher")
        ReviewService.publish_item(item.id)

        assert db.session.get(Concept, "concept-working-memory").status == "published"
        assert db.session.get(GraphEdge, "edge-working-memory-attention").status == "published"
        graph = CourseService.get_graph("brain-cog-intro")
        node_ids = {node["id"] for node in graph["nodes"]}
        edge_ids = {edge["id"] for edge in graph["edges"]}
        assert "concept-working-memory" in node_ids
        assert "edge-working-memory-attention" in edge_ids
```

- [ ] **Step 2: Run failing review test**

Run:

```bash
cd backend && uv run pytest app/tests/test_review_publish.py -q
```

Expected: FAIL because `ReviewItem` and `ReviewService` do not exist.

- [ ] **Step 3: Add ReviewItem model**

Append to `backend/app/models.py`:

```python
class ReviewItem(db.Model):
    id = db.Column(db.String, primary_key=True)
    title = db.Column(db.String, nullable=False)
    item_type = db.Column(db.String, nullable=False, default="graph_suggestion")
    status = db.Column(db.String, nullable=False, default="draft")
    payload_json = db.Column(db.Text, nullable=False, default="{}")
    reviewer = db.Column(db.String, nullable=False, default="")
    decision_notes = db.Column(db.Text, nullable=False, default="")
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)
```

- [ ] **Step 4: Implement review service**

Create `backend/app/services/review_service.py`:

```python
import json
from uuid import uuid4

from app.db import db
from app.models import Concept, GraphEdge, ReviewItem


class ReviewService:
    @staticmethod
    def list_items():
        return ReviewItem.query.order_by(ReviewItem.created_at.desc()).all()

    @staticmethod
    def create_graph_suggestion(title, payload):
        item = ReviewItem(
            id=f"review-{uuid4().hex}",
            title=title,
            item_type="graph_suggestion",
            status="draft",
            payload_json=json.dumps(payload, ensure_ascii=False),
        )
        db.session.add(item)
        db.session.commit()
        db.session.refresh(item)
        return item

    @staticmethod
    def get_payload(item):
        try:
            return json.loads(item.payload_json or "{}")
        except json.JSONDecodeError as exc:
            raise ValueError("Review payload must be valid JSON.") from exc

    @staticmethod
    def _ensure_draft(item, action):
        if item.status != "draft":
            raise ValueError(f"Only draft items can be {action}.")

    @staticmethod
    def _required_string(data, key, label):
        value = data.get(key)
        if not value:
            raise ValueError(f"{label} is required.")
        if not isinstance(value, str):
            raise ValueError(f"{label} must be a string.")
        return value

    @staticmethod
    def _optional_string(data, key, label):
        value = data.get(key, "")
        if value is None:
            return ""
        if not isinstance(value, str):
            raise ValueError(f"{label} must be a string.")
        return value

    @staticmethod
    def _validate_graph_payload(item):
        payload = ReviewService.get_payload(item)
        if not isinstance(payload, dict):
            raise ValueError("Review payload must be an object.")

        payload_course_id = payload.get("course_id")
        if payload_course_id is not None and not isinstance(payload_course_id, str):
            raise ValueError("Payload course_id must be a string.")
        concepts = payload.get("concepts", [])
        edges = payload.get("edges", [])
        if not isinstance(concepts, list):
            raise ValueError("Review payload concepts must be a list.")
        if not isinstance(edges, list):
            raise ValueError("Review payload edges must be a list.")

        normalized_concepts = []
        payload_concept_ids = set()
        for concept in payload.get("concepts", []):
            if not isinstance(concept, dict):
                raise ValueError("Each concept must be an object.")
            course_id = concept.get("course_id") or payload_course_id
            if course_id is not None and not isinstance(course_id, str):
                raise ValueError("Concept course_id must be a string.")
            concept_id = ReviewService._required_string(concept, "id", "Concept id")
            label = ReviewService._required_string(concept, "label", "Concept label")
            definition = ReviewService._optional_string(concept, "definition", "Concept definition")
            if not course_id:
                raise ValueError("Concept course_id is required.")
            normalized_concepts.append({
                "id": concept_id,
                "course_id": course_id,
                "label": label,
                "definition": definition,
            })
            payload_concept_ids.add(concept_id)

        normalized_edges = []
        for edge in payload.get("edges", []):
            if not isinstance(edge, dict):
                raise ValueError("Each edge must be an object.")
            course_id = edge.get("course_id") or payload_course_id
            if course_id is not None and not isinstance(course_id, str):
                raise ValueError("Edge course_id must be a string.")
            edge_id = ReviewService._required_string(edge, "id", "Edge id")
            source_id = ReviewService._required_string(edge, "source", "Edge source")
            target_id = ReviewService._required_string(edge, "target", "Edge target")
            relationship = ReviewService._required_string(edge, "relationship", "Edge relationship")
            evidence = ReviewService._optional_string(edge, "evidence", "Edge evidence")
            if not course_id:
                raise ValueError("Edge course_id is required.")
            for endpoint_name, concept_id in (("source", source_id), ("target", target_id)):
                if concept_id in payload_concept_ids:
                    continue
                concept = db.session.get(Concept, concept_id)
                if concept is None:
                    raise ValueError(f"Edge {endpoint_name} concept does not exist: {concept_id}")
                if concept.status != "published":
                    raise ValueError(f"Edge {endpoint_name} concept is not published: {concept_id}")
            normalized_edges.append({
                "id": edge_id,
                "course_id": course_id,
                "source_id": source_id,
                "target_id": target_id,
                "relationship": relationship,
                "evidence": evidence,
            })

        return normalized_concepts, normalized_edges

    @staticmethod
    def approve_item(item_id, reviewer="", notes=""):
        item = db.get_or_404(ReviewItem, item_id)
        ReviewService._ensure_draft(item, "approved")
        reviewer = ReviewService._optional_string({"reviewer": reviewer}, "reviewer", "Reviewer")
        notes = ReviewService._optional_string({"notes": notes}, "notes", "Decision notes")
        item.status = "reviewed"
        item.reviewer = reviewer
        item.decision_notes = notes
        db.session.commit()
        return item

    @staticmethod
    def reject_item(item_id, reviewer="", notes=""):
        item = db.get_or_404(ReviewItem, item_id)
        ReviewService._ensure_draft(item, "rejected")
        reviewer = ReviewService._optional_string({"reviewer": reviewer}, "reviewer", "Reviewer")
        notes = ReviewService._optional_string({"notes": notes}, "notes", "Decision notes")
        item.status = "rejected"
        item.reviewer = reviewer
        item.decision_notes = notes
        db.session.commit()
        return item

    @staticmethod
    def publish_item(item_id):
        item = db.get_or_404(ReviewItem, item_id)
        if item.status != "reviewed":
            raise ValueError("Only reviewed items can be published.")

        concepts, edges = ReviewService._validate_graph_payload(item)
        try:
            for concept in concepts:
                db.session.merge(Concept(
                    id=concept["id"],
                    course_id=concept["course_id"],
                    label=concept["label"],
                    definition=concept["definition"],
                    status="published",
                ))
            for edge in edges:
                db.session.merge(GraphEdge(
                    id=edge["id"],
                    course_id=edge["course_id"],
                    source_id=edge["source_id"],
                    target_id=edge["target_id"],
                    relationship=edge["relationship"],
                    evidence=edge["evidence"],
                    status="published",
                ))
            item.status = "published"
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        return item
```

- [ ] **Step 5: Implement review API**

Create `backend/app/api/review.py`:

```python
from flask import jsonify, request

from app.api import api_bp
from app.services.review_service import ReviewService


def _serialize(item):
    return {
        "id": item.id,
        "title": item.title,
        "item_type": item.item_type,
        "status": item.status,
        "payload": ReviewService.get_payload(item),
        "reviewer": item.reviewer,
        "decision_notes": item.decision_notes,
    }


def _error_response(exc):
    return jsonify({"success": False, "error": str(exc)}), 400


def _request_body():
    data = request.get_json(silent=True)
    if data is None:
        data = {}
    if not isinstance(data, dict):
        raise ValueError("Request body must be an object.")
    return data


@api_bp.get("/review/items")
def list_review_items():
    return jsonify({"success": True, "data": [_serialize(item) for item in ReviewService.list_items()]})


@api_bp.post("/review/items/<item_id>/approve")
def approve_review_item(item_id):
    try:
        data = _request_body()
        item = ReviewService.approve_item(item_id, reviewer=data.get("reviewer", ""), notes=data.get("notes", ""))
    except ValueError as exc:
        return _error_response(exc)
    return jsonify({"success": True, "data": _serialize(item)})


@api_bp.post("/review/items/<item_id>/reject")
def reject_review_item(item_id):
    try:
        data = _request_body()
        item = ReviewService.reject_item(item_id, reviewer=data.get("reviewer", ""), notes=data.get("notes", ""))
    except ValueError as exc:
        return _error_response(exc)
    return jsonify({"success": True, "data": _serialize(item)})


@api_bp.post("/review/items/<item_id>/publish")
def publish_review_item(item_id):
    try:
        item = ReviewService.publish_item(item_id)
    except ValueError as exc:
        return _error_response(exc)
    return jsonify({"success": True, "data": _serialize(item)})
```

Modify `backend/app/api/__init__.py`:

```python
from flask import Blueprint, jsonify
from werkzeug.exceptions import NotFound

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.errorhandler(NotFound)
def handle_not_found(error):
    return jsonify({"success": False, "error": error.description}), 404


from . import courses  # noqa: E402,F401
from . import graph  # noqa: E402,F401
from . import review  # noqa: E402,F401
```

- [ ] **Step 6: Run review tests**

Run:

```bash
cd backend && uv run pytest app/tests/test_review_publish.py -q
```

Expected: PASS.

- [ ] **Step 7: Commit**

Run:

```bash
git add backend/app/models.py backend/app/services/review_service.py backend/app/api/review.py backend/app/api/__init__.py backend/app/tests/test_review_publish.py
git commit -m "feat: add teacher review publish workflow"
```

Expected: commit succeeds.

---

### Task 5: Material Upload And Draft Extraction

**Files:**
- Modify: `backend/app/models.py`
- Create: `backend/app/services/material_service.py`
- Create: `backend/app/api/materials.py`
- Modify: `backend/app/api/__init__.py`

- [ ] **Step 1: Add material and chunk models**

Append to `backend/app/models.py`:

```python
class Material(db.Model):
    id = db.Column(db.String, primary_key=True)
    course_id = db.Column(db.String, db.ForeignKey("course.id"), nullable=False)
    filename = db.Column(db.String, nullable=False)
    path = db.Column(db.String, nullable=False)
    parser_status = db.Column(db.String, nullable=False, default="uploaded")
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)


class Chunk(db.Model):
    id = db.Column(db.String, primary_key=True)
    material_id = db.Column(db.String, db.ForeignKey("material.id"), nullable=False)
    text = db.Column(db.Text, nullable=False)
    citation_locator = db.Column(db.String, nullable=False, default="")
```

- [ ] **Step 2: Implement material service**

Create `backend/app/services/material_service.py`:

```python
import os
import re
import uuid

from werkzeug.utils import secure_filename

from app.config import Config
from app.db import db
from app.models import Chunk, Material
from app.services.review_service import ReviewService


class MaterialService:
    @staticmethod
    def save_upload(course_id, file_storage):
        os.makedirs(Config.UPLOAD_DIR, exist_ok=True)
        safe_name = secure_filename(file_storage.filename or "material.txt")
        material_id = f"material_{uuid.uuid4().hex[:12]}"
        path = os.path.join(Config.UPLOAD_DIR, f"{material_id}_{safe_name}")
        file_storage.save(path)

        material = Material(id=material_id, course_id=course_id, filename=safe_name, path=path, parser_status="uploaded")
        db.session.add(material)
        db.session.commit()
        return material

    @staticmethod
    def extract_text(material):
        with open(material.path, "rb") as f:
            raw = f.read()
        return raw.decode("utf-8", errors="ignore")

    @staticmethod
    def chunk_material(material):
        text = MaterialService.extract_text(material)
        pieces = [piece.strip() for piece in re.split(r"\n\s*\n", text) if piece.strip()]
        if not pieces and text.strip():
            pieces = [text.strip()]
        chunks = []
        for index, piece in enumerate(pieces[:20], start=1):
            chunk = Chunk(id=f"chunk_{uuid.uuid4().hex[:12]}", material_id=material.id, text=piece[:1200], citation_locator=f"{material.filename}#chunk-{index}")
            db.session.add(chunk)
            chunks.append(chunk)
        material.parser_status = "chunked"
        db.session.commit()
        return chunks

    @staticmethod
    def create_review_suggestion_from_material(material):
        chunks = MaterialService.chunk_material(material)
        title = f"Review extracted concepts from {material.filename}"
        payload = {
            "concepts": [
                {
                    "id": f"concept-upload-{material.id}",
                    "label": material.filename.rsplit(".", 1)[0],
                    "definition": chunks[0].text[:240] if chunks else "Uploaded course material.",
                }
            ],
            "edges": [],
        }
        return ReviewService.create_graph_suggestion(title=title, payload=payload)
```

- [ ] **Step 3: Implement material API**

Create `backend/app/api/materials.py`:

```python
from flask import jsonify, request

from app.api import api_bp
from app.models import Material
from app.services.material_service import MaterialService


@api_bp.post("/materials/upload")
def upload_material():
    course_id = request.form.get("course_id")
    file_storage = request.files.get("file")
    if not course_id or not file_storage:
        return jsonify({"success": False, "error": "course_id and file are required"}), 400
    material = MaterialService.save_upload(course_id, file_storage)
    review_item = MaterialService.create_review_suggestion_from_material(material)
    return jsonify({
        "success": True,
        "data": {
            "material": {"id": material.id, "course_id": material.course_id, "filename": material.filename, "parser_status": material.parser_status},
            "review_item_id": review_item.id,
        },
    })


@api_bp.get("/materials")
def list_materials():
    course_id = request.args.get("course_id")
    query = Material.query
    if course_id:
        query = query.filter_by(course_id=course_id)
    return jsonify({
        "success": True,
        "data": [{"id": item.id, "course_id": item.course_id, "filename": item.filename, "parser_status": item.parser_status} for item in query.all()],
    })
```

Modify `backend/app/api/__init__.py`:

```python
from flask import Blueprint, jsonify
from werkzeug.exceptions import NotFound

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.errorhandler(NotFound)
def handle_not_found(error):
    return jsonify({"success": False, "error": error.description}), 404


from . import courses  # noqa: E402,F401
from . import graph  # noqa: E402,F401
from . import review  # noqa: E402,F401
from . import materials  # noqa: E402,F401
```

- [ ] **Step 4: Smoke test material upload**

Run:

```bash
cd backend && uv run pytest -q
```

Expected: existing tests PASS.

- [ ] **Step 5: Commit**

Run:

```bash
git add backend/app/models.py backend/app/services/material_service.py backend/app/api/materials.py backend/app/api/__init__.py
git commit -m "feat: add material upload draft extraction"
```

Expected: commit succeeds.

---

### Task 6: Cited AI Tutor Service

**Files:**
- Create: `backend/app/services/tutor_service.py`
- Create: `backend/app/api/tutor.py`
- Modify: `backend/app/api/__init__.py`
- Create: `backend/app/tests/test_tutor_service.py`

- [ ] **Step 1: Write tutor service tests**

Create `backend/app/tests/test_tutor_service.py`:

```python
from app.services.seed_data import seed_courses
from app.services.tutor_service import TutorService


def test_tutor_returns_citations_for_known_question(app):
    with app.app_context():
        seed_courses()
        result = TutorService.answer(question="How are transformer attention and human attention related?", course_id="ai-intro")

    assert "citations" in result
    assert result["citations"]
    assert "attention" in result["answer"].lower()


def test_tutor_qualifies_unknown_question(app):
    with app.app_context():
        seed_courses()
        result = TutorService.answer(question="What is the tuition refund policy?", course_id="ai-intro")

    assert result["insufficient_evidence"] is True
```

- [ ] **Step 2: Run failing tutor tests**

Run:

```bash
cd backend && uv run pytest app/tests/test_tutor_service.py -q
```

Expected: FAIL because tutor service does not exist.

- [ ] **Step 3: Implement deterministic MVP tutor**

Create `backend/app/services/tutor_service.py`:

```python
from app.db import db
from app.models import Chapter, Concept
from app.services.course_service import CourseService


class TutorService:
    @staticmethod
    def answer(question, course_id=None, chapter_id=None, concept_id=None):
        query = question.lower()
        evidence = []
        graph = CourseService.get_graph(course_id)
        graph_concept_ids = {node["id"] for node in graph["nodes"]}

        concept_query = Concept.query.filter_by(status="published")
        if concept_id:
            concept_query = concept_query.filter_by(id=concept_id)
        elif course_id:
            concept_query = concept_query.filter(Concept.id.in_(graph_concept_ids))

        concepts = concept_query.all()
        for concept in concepts:
            haystack = f"{concept.label} {concept.definition}".lower()
            if any(token in haystack for token in query.split() if len(token) > 4):
                evidence.append({
                    "type": "concept",
                    "id": concept.id,
                    "title": concept.label,
                    "snippet": concept.definition,
                })

        evidence_ids = {item["id"] for item in evidence}
        for edge in graph["edges"]:
            if evidence_ids and (edge["source"] in evidence_ids or edge["target"] in evidence_ids):
                evidence.append({
                    "type": "graph_edge",
                    "id": edge["id"],
                    "title": edge["relationship"],
                    "snippet": edge["evidence"],
                })

        if chapter_id:
            chapter = db.session.get(Chapter, chapter_id)
            if chapter:
                evidence.append({
                    "type": "chapter",
                    "id": chapter.id,
                    "title": chapter.title,
                    "snippet": chapter.body[:240],
                })

        if not evidence:
            return {
                "answer": "I do not have enough published course evidence to answer that reliably.",
                "citations": [],
                "insufficient_evidence": True,
            }

        answer = "Based on the published course graph, " + " ".join(item["snippet"] for item in evidence[:3] if item["snippet"])
        return {
            "answer": answer[:800],
            "citations": evidence[:5],
            "insufficient_evidence": False,
        }
```

- [ ] **Step 4: Implement tutor API**

Create `backend/app/api/tutor.py`:

```python
from flask import jsonify, request

from app.api import api_bp
from app.services.tutor_service import TutorService


@api_bp.post("/tutor/ask")
def ask_tutor():
    data = request.get_json() or {}
    question = (data.get("question") or "").strip()
    if not question:
        return jsonify({"success": False, "error": "question is required"}), 400
    result = TutorService.answer(
        question=question,
        course_id=data.get("course_id"),
        chapter_id=data.get("chapter_id"),
        concept_id=data.get("concept_id"),
    )
    return jsonify({"success": True, "data": result})
```

Modify `backend/app/api/__init__.py`:

```python
from flask import Blueprint, jsonify
from werkzeug.exceptions import NotFound

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.errorhandler(NotFound)
def handle_not_found(error):
    return jsonify({"success": False, "error": error.description}), 404


from . import courses  # noqa: E402,F401
from . import graph  # noqa: E402,F401
from . import review  # noqa: E402,F401
from . import materials  # noqa: E402,F401
from . import tutor  # noqa: E402,F401
```

- [ ] **Step 5: Run tutor tests**

Run:

```bash
cd backend && uv run pytest app/tests/test_tutor_service.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit**

Run:

```bash
git add backend/app/services/tutor_service.py backend/app/api/tutor.py backend/app/api/__init__.py backend/app/tests/test_tutor_service.py
git commit -m "feat: add cited tutor service"
```

Expected: commit succeeds.

---

### Task 7: Vue Frontend Skeleton

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/index.html`
- Create: `frontend/vite.config.js`
- Create: `frontend/src/main.js`
- Create: `frontend/src/App.vue`
- Create: `frontend/src/router/index.js`
- Create: `frontend/src/styles/app.css`
- Create: `frontend/src/api/client.js`

- [ ] **Step 1: Create frontend package**

Create `frontend/package.json`:

```json
{
  "name": "cognitive-ai-learning-platform-frontend",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite --host 0.0.0.0",
    "build": "vite build",
    "preview": "vite preview",
    "test": "vitest run"
  },
  "dependencies": {
    "@vitejs/plugin-vue": "^6.0.1",
    "axios": "^1.14.0",
    "d3": "^7.9.0",
    "pinia": "^3.0.4",
    "vue": "^3.5.24",
    "vue-router": "^4.6.3"
  },
  "devDependencies": {
    "vite": "^7.2.4",
    "vitest": "^4.0.0"
  }
}
```

Create `frontend/index.html`:

```html
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Cognitive AI Learning Platform</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.js"></script>
  </body>
</html>
```

Create `frontend/vite.config.js`:

```js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    proxy: {
      '/api': 'http://127.0.0.1:5001',
      '/health': 'http://127.0.0.1:5001'
    }
  }
})
```

- [ ] **Step 2: Create app shell**

Create `frontend/src/main.js`:

```js
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './styles/app.css'

createApp(App).use(createPinia()).use(router).mount('#app')
```

Create `frontend/src/App.vue`:

```vue
<template>
  <div class="app-shell">
    <aside class="sidebar">
      <div class="brand">Cognitive AI</div>
      <RouterLink to="/">Dashboard</RouterLink>
      <RouterLink to="/courses/ai-intro">Courses</RouterLink>
      <RouterLink to="/teacher">Teacher Studio</RouterLink>
    </aside>
    <main class="main">
      <RouterView />
    </main>
  </div>
</template>
```

Create `frontend/src/router/index.js`:

```js
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', component: () => import('../views/DashboardView.vue') },
  { path: '/courses/:courseId', component: () => import('../views/CourseView.vue'), props: true },
  { path: '/teacher', component: () => import('../views/TeacherStudioView.vue') }
]

export default createRouter({
  history: createWebHistory(),
  routes
})
```

Create `frontend/src/api/client.js`:

```js
import axios from 'axios'

export const api = axios.create({
  baseURL: '',
  timeout: 20000
})

export function unwrap(response) {
  if (!response.data?.success) {
    throw new Error(response.data?.error || 'Request failed')
  }
  return response.data.data
}
```

Create `frontend/src/styles/app.css`:

```css
* { box-sizing: border-box; }
body { margin: 0; font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #f6f7f9; color: #17202a; }
a { color: inherit; text-decoration: none; }
.app-shell { min-height: 100vh; display: grid; grid-template-columns: 240px 1fr; }
.sidebar { background: #111827; color: #fff; padding: 20px; display: flex; flex-direction: column; gap: 12px; }
.brand { font-weight: 700; margin-bottom: 20px; }
.sidebar a { padding: 10px 12px; border-radius: 6px; color: #d1d5db; }
.sidebar a.router-link-active { background: #2563eb; color: #fff; }
.main { padding: 24px; min-width: 0; }
.panel { background: #fff; border: 1px solid #e5e7eb; border-radius: 8px; padding: 16px; }
.grid { display: grid; gap: 16px; }
.two-col { grid-template-columns: minmax(0, 1fr) 380px; }
button { min-height: 40px; border: 0; border-radius: 6px; padding: 0 14px; background: #2563eb; color: #fff; cursor: pointer; }
input, textarea, select { width: 100%; min-height: 40px; border: 1px solid #d1d5db; border-radius: 6px; padding: 8px 10px; font: inherit; }
```

- [ ] **Step 3: Commit frontend skeleton**

Run:

```bash
git add frontend
git commit -m "chore: scaffold vue frontend"
```

Expected: commit succeeds.

---

### Task 8: Student Course Workspace

**Files:**
- Create: `frontend/src/api/courses.js`
- Create: `frontend/src/api/graph.js`
- Create: `frontend/src/api/tutor.js`
- Create: `frontend/src/views/DashboardView.vue`
- Create: `frontend/src/views/CourseView.vue`
- Create: `frontend/src/components/ChapterWorkspace.vue`
- Create: `frontend/src/components/AITutorPanel.vue`

- [ ] **Step 1: Create frontend API wrappers**

Create `frontend/src/api/courses.js`:

```js
import { api, unwrap } from './client'

export const listCourses = () => api.get('/api/courses').then(unwrap)
export const getCourse = (courseId) => api.get(`/api/courses/${courseId}`).then(unwrap)
export const getChapter = (chapterId) => api.get(`/api/chapters/${chapterId}`).then(unwrap)
```

Create `frontend/src/api/graph.js`:

```js
import { api, unwrap } from './client'

export const getGraph = (courseId) => api.get('/api/graph', { params: { course_id: courseId } }).then(unwrap)
```

Create `frontend/src/api/tutor.js`:

```js
import { api, unwrap } from './client'

export const askTutor = (payload) => api.post('/api/tutor/ask', payload).then(unwrap)
```

- [ ] **Step 2: Create dashboard and course view**

Create `frontend/src/views/DashboardView.vue`:

```vue
<template>
  <div class="grid">
    <h1>Course Dashboard</h1>
    <div class="panel" v-for="course in courses" :key="course.id">
      <h2>{{ course.title }}</h2>
      <p>{{ course.summary }}</p>
      <RouterLink :to="`/courses/${course.id}`">Open course</RouterLink>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { listCourses } from '../api/courses'

const courses = ref([])

onMounted(async () => {
  courses.value = await listCourses()
})
</script>
```

Create `frontend/src/views/CourseView.vue`:

```vue
<template>
  <div class="grid two-col">
    <section class="grid">
      <div class="panel">
        <h1>{{ course?.title }}</h1>
        <p>{{ course?.summary }}</p>
      </div>
      <ChapterWorkspace
        v-if="activeChapter"
        :chapter="activeChapter"
        @select-question="question => tutorQuestion = question"
      />
    </section>
    <aside class="grid">
      <div class="panel">
        <h2>Chapters</h2>
        <button v-for="chapter in course?.chapters || []" :key="chapter.id" @click="loadChapter(chapter.id)">
          {{ chapter.title }}
        </button>
      </div>
      <AITutorPanel :course-id="courseId" :chapter-id="activeChapter?.id" :initial-question="tutorQuestion" />
    </aside>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { getChapter, getCourse } from '../api/courses'
import AITutorPanel from '../components/AITutorPanel.vue'
import ChapterWorkspace from '../components/ChapterWorkspace.vue'

const props = defineProps({ courseId: String })
const course = ref(null)
const activeChapter = ref(null)
const tutorQuestion = ref('')

async function loadChapter(chapterId) {
  activeChapter.value = await getChapter(chapterId)
}

onMounted(async () => {
  course.value = await getCourse(props.courseId)
  if (course.value.chapters?.[0]) await loadChapter(course.value.chapters[0].id)
})

watch(() => props.courseId, async () => {
  course.value = await getCourse(props.courseId)
  if (course.value.chapters?.[0]) await loadChapter(course.value.chapters[0].id)
})
</script>
```

- [ ] **Step 3: Create chapter and tutor components**

Create `frontend/src/components/ChapterWorkspace.vue`:

```vue
<template>
  <article class="panel">
    <h2>{{ chapter.title }}</h2>
    <p><strong>Objectives:</strong> {{ chapter.objectives }}</p>
    <p>{{ chapter.body }}</p>
    <h3>Mastery Check</h3>
    <div v-for="item in chapter.quiz_items" :key="item.id" class="panel">
      <p>{{ item.prompt }}</p>
      <button @click="$emit('select-question', item.prompt)">Ask AI tutor</button>
      <details>
        <summary>Show answer</summary>
        <p>{{ item.answer }}</p>
        <p>{{ item.explanation }}</p>
      </details>
    </div>
  </article>
</template>

<script setup>
defineProps({ chapter: { type: Object, required: true } })
defineEmits(['select-question'])
</script>
```

Create `frontend/src/components/AITutorPanel.vue`:

```vue
<template>
  <div class="panel">
    <h2>AI Tutor</h2>
    <textarea v-model="question" placeholder="Ask a course-grounded question"></textarea>
    <button @click="submit" :disabled="loading">{{ loading ? 'Thinking...' : 'Ask' }}</button>
    <div v-if="answer" class="panel">
      <p>{{ answer.answer }}</p>
      <h3>Citations</h3>
      <ul>
        <li v-for="citation in answer.citations" :key="citation.id">
          {{ citation.type }}: {{ citation.title }} - {{ citation.snippet }}
        </li>
      </ul>
      <p v-if="answer.insufficient_evidence">Evidence is insufficient for a reliable answer.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { askTutor } from '../api/tutor'

const props = defineProps({
  courseId: String,
  chapterId: String,
  initialQuestion: String
})

const question = ref('')
const answer = ref(null)
const loading = ref(false)

watch(() => props.initialQuestion, value => {
  if (value) question.value = value
})

async function submit() {
  if (!question.value.trim()) return
  loading.value = true
  try {
    answer.value = await askTutor({ question: question.value, course_id: props.courseId, chapter_id: props.chapterId })
  } finally {
    loading.value = false
  }
}
</script>
```

- [ ] **Step 4: Build frontend**

Run:

```bash
cd frontend && npm install && npm run build
```

Expected: Vite build succeeds.

- [ ] **Step 5: Commit**

Run:

```bash
git add frontend/src frontend/package.json frontend/index.html frontend/vite.config.js
git commit -m "feat: add student course workspace"
```

Expected: commit succeeds.

---

### Task 9: MiroFish-Style Graph Panel

**Files:**
- Create: `frontend/src/components/GraphPanel.vue`
- Modify: `frontend/src/views/CourseView.vue`
- Create: `frontend/tests/unit/graphTransform.test.js`

- [ ] **Step 1: Create graph transform unit test**

Create `frontend/tests/unit/graphTransform.test.js`:

```js
import { describe, expect, it } from 'vitest'

function toGraphStats(graph) {
  return {
    nodeCount: graph.nodes.length,
    edgeCount: graph.edges.length,
    types: [...new Set(graph.nodes.map(node => node.type))]
  }
}

describe('graph stats', () => {
  it('counts nodes, edges, and types', () => {
    const stats = toGraphStats({
      nodes: [{ id: 'a', type: 'Concept' }, { id: 'b', type: 'Chapter' }],
      edges: [{ id: 'e1', source: 'a', target: 'b' }]
    })
    expect(stats.nodeCount).toBe(2)
    expect(stats.edgeCount).toBe(1)
    expect(stats.types).toEqual(['Concept', 'Chapter'])
  })
})
```

- [ ] **Step 2: Implement graph panel**

Create `frontend/src/components/GraphPanel.vue`:

```vue
<template>
  <div class="panel graph-panel">
    <div class="graph-toolbar">
      <strong>Knowledge Graph</strong>
      <input v-model="search" placeholder="Search concepts" />
      <label><input type="checkbox" v-model="showLabels" /> Edge labels</label>
    </div>
    <svg ref="svgRef" class="graph-svg"></svg>
    <div v-if="selected" class="graph-detail">
      <button @click="selected = null">Close</button>
      <h3>{{ selected.label || selected.relationship }}</h3>
      <p>{{ selected.definition || selected.evidence }}</p>
    </div>
    <div class="graph-mini">
      {{ graph.nodes.length }} nodes · {{ graph.edges.length }} edges
    </div>
  </div>
</template>

<script setup>
import * as d3 from 'd3'
import { nextTick, onMounted, ref, watch } from 'vue'

const props = defineProps({
  graph: { type: Object, default: () => ({ nodes: [], edges: [] }) }
})

const svgRef = ref(null)
const selected = ref(null)
const search = ref('')
const showLabels = ref(true)

function render() {
  if (!svgRef.value) return
  const width = svgRef.value.clientWidth || 720
  const height = 420
  const svg = d3.select(svgRef.value).attr('viewBox', `0 0 ${width} ${height}`)
  svg.selectAll('*').remove()

  const nodes = props.graph.nodes.map(node => ({ ...node }))
  const edges = props.graph.edges.map(edge => ({ ...edge }))
  const nodeIds = new Set(nodes.map(node => node.id))
  const validEdges = edges.filter(edge => nodeIds.has(edge.source) && nodeIds.has(edge.target))

  const color = d3.scaleOrdinal().domain(['Course', 'Chapter', 'Concept', 'Material']).range(['#2563eb', '#059669', '#d97706', '#7c3aed'])
  const root = svg.append('g')
  svg.call(d3.zoom().scaleExtent([0.2, 4]).on('zoom', event => root.attr('transform', event.transform)))

  const simulation = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(validEdges).id(d => d.id).distance(120))
    .force('charge', d3.forceManyBody().strength(-360))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('collide', d3.forceCollide(36))

  const link = root.append('g').selectAll('line').data(validEdges).enter().append('line')
    .attr('stroke', '#9ca3af')
    .attr('stroke-width', 1.4)
    .on('click', (_, edge) => { selected.value = edge })

  const labels = root.append('g').selectAll('text.edge-label').data(validEdges).enter().append('text')
    .attr('class', 'edge-label')
    .attr('font-size', 9)
    .attr('fill', '#4b5563')
    .text(edge => edge.relationship)

  const node = root.append('g').selectAll('circle').data(nodes).enter().append('circle')
    .attr('r', 12)
    .attr('fill', node => color(node.type || 'Concept'))
    .attr('stroke', '#fff')
    .attr('stroke-width', 2)
    .call(d3.drag()
      .on('start', event => { if (!event.active) simulation.alphaTarget(0.3).restart() })
      .on('drag', (event, node) => { node.fx = event.x; node.fy = event.y })
      .on('end', (event, node) => { if (!event.active) simulation.alphaTarget(0); node.fx = null; node.fy = null })
    )
    .on('click', (_, node) => { selected.value = node })

  const nodeLabels = root.append('g').selectAll('text.node-label').data(nodes).enter().append('text')
    .attr('class', 'node-label')
    .attr('font-size', 11)
    .attr('dx', 16)
    .attr('dy', 4)
    .text(node => node.label)

  simulation.on('tick', () => {
    link.attr('x1', d => d.source.x).attr('y1', d => d.source.y).attr('x2', d => d.target.x).attr('y2', d => d.target.y)
    labels.attr('x', d => (d.source.x + d.target.x) / 2).attr('y', d => (d.source.y + d.target.y) / 2).style('display', showLabels.value ? 'block' : 'none')
    node.attr('cx', d => d.x).attr('cy', d => d.y)
    nodeLabels.attr('x', d => d.x).attr('y', d => d.y)
  })
}

watch(() => props.graph, () => nextTick(render), { deep: true })
watch(showLabels, () => nextTick(render))
onMounted(() => nextTick(render))
</script>

<style scoped>
.graph-panel { position: relative; min-height: 520px; }
.graph-toolbar { display: grid; grid-template-columns: auto 1fr auto; gap: 12px; align-items: center; margin-bottom: 12px; }
.graph-svg { width: 100%; height: 420px; background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; }
.graph-detail { position: absolute; top: 72px; right: 24px; width: 280px; background: white; border: 1px solid #d1d5db; border-radius: 8px; padding: 12px; box-shadow: 0 16px 40px rgba(15,23,42,.16); }
.graph-mini { position: absolute; left: 28px; bottom: 22px; background: white; border: 1px solid #d1d5db; border-radius: 6px; padding: 6px 10px; font-size: 12px; }
```

- [ ] **Step 3: Mount graph in CourseView**

Modify `frontend/src/views/CourseView.vue` to fetch and display graph below the chapter:

```vue
<template>
  <div class="grid two-col">
    <section class="grid">
      <div class="panel">
        <h1>{{ course?.title }}</h1>
        <p>{{ course?.summary }}</p>
      </div>
      <ChapterWorkspace
        v-if="activeChapter"
        :chapter="activeChapter"
        @select-question="question => tutorQuestion = question"
      />
      <GraphPanel :graph="graph" />
    </section>
    <aside class="grid">
      <div class="panel">
        <h2>Chapters</h2>
        <button v-for="chapter in course?.chapters || []" :key="chapter.id" @click="loadChapter(chapter.id)">
          {{ chapter.title }}
        </button>
      </div>
      <AITutorPanel :course-id="courseId" :chapter-id="activeChapter?.id" :initial-question="tutorQuestion" />
    </aside>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { getChapter, getCourse } from '../api/courses'
import { getGraph } from '../api/graph'
import AITutorPanel from '../components/AITutorPanel.vue'
import ChapterWorkspace from '../components/ChapterWorkspace.vue'
import GraphPanel from '../components/GraphPanel.vue'

const props = defineProps({ courseId: String })
const course = ref(null)
const activeChapter = ref(null)
const tutorQuestion = ref('')
const graph = ref({ nodes: [], edges: [] })

async function loadChapter(chapterId) {
  activeChapter.value = await getChapter(chapterId)
}

async function loadCourse() {
  course.value = await getCourse(props.courseId)
  graph.value = await getGraph(props.courseId)
  if (course.value.chapters?.[0]) await loadChapter(course.value.chapters[0].id)
}

onMounted(loadCourse)
watch(() => props.courseId, loadCourse)
</script>
```

- [ ] **Step 4: Test and build frontend**

Run:

```bash
cd frontend && npm test && npm run build
```

Expected: Vitest and Vite build PASS.

- [ ] **Step 5: Commit**

Run:

```bash
git add frontend/src/components/GraphPanel.vue frontend/src/views/CourseView.vue frontend/tests/unit/graphTransform.test.js
git commit -m "feat: add knowledge graph panel"
```

Expected: commit succeeds.

---

### Task 10: Teacher Studio Review UI

**Files:**
- Create: `frontend/src/api/review.js`
- Create: `frontend/src/api/materials.js`
- Create: `frontend/src/views/TeacherStudioView.vue`
- Create: `frontend/src/components/ReviewQueue.vue`

- [ ] **Step 1: Create review and material API wrappers**

Create `frontend/src/api/review.js`:

```js
import { api, unwrap } from './client'

export const listReviewItems = () => api.get('/api/review/items').then(unwrap)
export const approveReviewItem = (id) => api.post(`/api/review/items/${id}/approve`, { reviewer: 'teacher' }).then(unwrap)
export const rejectReviewItem = (id) => api.post(`/api/review/items/${id}/reject`, { reviewer: 'teacher' }).then(unwrap)
export const publishReviewItem = (id) => api.post(`/api/review/items/${id}/publish`).then(unwrap)
```

Create `frontend/src/api/materials.js`:

```js
import { api, unwrap } from './client'

export const uploadMaterial = (courseId, file) => {
  const formData = new FormData()
  formData.append('course_id', courseId)
  formData.append('file', file)
  return api.post('/api/materials/upload', formData).then(unwrap)
}
```

- [ ] **Step 2: Create review queue component**

Create `frontend/src/components/ReviewQueue.vue`:

```vue
<template>
  <div class="panel">
    <h2>Review Queue</h2>
    <div v-if="!items.length">No pending review items.</div>
    <article v-for="item in items" :key="item.id" class="panel">
      <h3>{{ item.title }}</h3>
      <p>Status: {{ item.status }}</p>
      <pre>{{ JSON.stringify(item.payload, null, 2) }}</pre>
      <button @click="$emit('approve', item.id)" v-if="item.status === 'draft'">Approve</button>
      <button @click="$emit('reject', item.id)" v-if="item.status === 'draft'">Reject</button>
      <button @click="$emit('publish', item.id)" v-if="item.status === 'reviewed'">Publish</button>
    </article>
  </div>
</template>

<script setup>
defineProps({ items: { type: Array, default: () => [] } })
defineEmits(['approve', 'reject', 'publish'])
</script>

<style scoped>
pre { white-space: pre-wrap; background: #f3f4f6; padding: 12px; border-radius: 6px; overflow: auto; }
article { margin-top: 12px; }
button + button { margin-left: 8px; }
</style>
```

- [ ] **Step 3: Create Teacher Studio view**

Create `frontend/src/views/TeacherStudioView.vue`:

```vue
<template>
  <div class="grid">
    <h1>Teacher Studio</h1>
    <section class="panel">
      <h2>Upload material</h2>
      <select v-model="courseId">
        <option v-for="course in courses" :key="course.id" :value="course.id">{{ course.title }}</option>
      </select>
      <input type="file" @change="event => selectedFile = event.target.files[0]" />
      <button @click="submitUpload" :disabled="!selectedFile || uploading">{{ uploading ? 'Uploading...' : 'Upload and Extract Draft' }}</button>
      <p v-if="message">{{ message }}</p>
    </section>
    <ReviewQueue :items="reviewItems" @approve="approve" @reject="reject" @publish="publish" />
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { listCourses } from '../api/courses'
import { uploadMaterial } from '../api/materials'
import { approveReviewItem, listReviewItems, publishReviewItem, rejectReviewItem } from '../api/review'
import ReviewQueue from '../components/ReviewQueue.vue'

const courses = ref([])
const courseId = ref('ai-intro')
const selectedFile = ref(null)
const uploading = ref(false)
const message = ref('')
const reviewItems = ref([])

async function refresh() {
  reviewItems.value = await listReviewItems()
}

async function submitUpload() {
  uploading.value = true
  try {
    const result = await uploadMaterial(courseId.value, selectedFile.value)
    message.value = `Created review item ${result.review_item_id}`
    await refresh()
  } finally {
    uploading.value = false
  }
}

async function approve(id) {
  await approveReviewItem(id)
  await refresh()
}

async function reject(id) {
  await rejectReviewItem(id)
  await refresh()
}

async function publish(id) {
  await publishReviewItem(id)
  await refresh()
}

onMounted(async () => {
  courses.value = await listCourses()
  if (courses.value[0]) courseId.value = courses.value[0].id
  await refresh()
})
</script>
```

- [ ] **Step 4: Build frontend**

Run:

```bash
cd frontend && npm run build
```

Expected: Vite build PASS.

- [ ] **Step 5: Commit**

Run:

```bash
git add frontend/src/api/review.js frontend/src/api/materials.js frontend/src/views/TeacherStudioView.vue frontend/src/components/ReviewQueue.vue
git commit -m "feat: add teacher studio review ui"
```

Expected: commit succeeds.

---

### Task 11: End-To-End Verification

**Files:**
- Modify only if verification exposes defects in files already created by previous tasks.

- [ ] **Step 1: Run backend test suite**

Run:

```bash
cd backend && uv run pytest -q
```

Expected: all backend tests PASS.

- [ ] **Step 2: Run frontend tests and build**

Run:

```bash
cd frontend && npm test && npm run build
```

Expected: Vitest PASS and Vite build PASS.

- [ ] **Step 3: Run local app smoke test**

Start backend:

```bash
cd backend && uv run python run.py
```

Start frontend in another shell:

```bash
cd frontend && npm run dev
```

Open:

```text
http://localhost:3000
```

Verify manually:

- Dashboard shows the two seeded courses.
- Opening `人工智能导论` shows chapter content.
- AI tutor answers an attention-related question with citations.
- Knowledge graph renders nodes and edges.
- Teacher Studio uploads a `.txt` file and creates a review item.
- Approving and publishing the review item updates `/api/graph`.

- [ ] **Step 4: Commit verification fixes**

If fixes were needed:

```bash
git add backend frontend
git commit -m "fix: stabilize mvp smoke flow"
```

If no fixes were needed, skip this commit and record the passing commands in the final implementation summary.

---

### Task 12: Documentation And Handoff

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Update README run instructions**

Update `README.md`:

```markdown
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
```

- [ ] **Step 2: Run all verification**

Run:

```bash
cd backend && uv run pytest -q
cd ../frontend && npm test && npm run build
```

Expected: all tests and build PASS.

- [ ] **Step 3: Final commit**

Run:

```bash
git add README.md
git commit -m "docs: add mvp setup and verification guide"
```

Expected: commit succeeds.

---

## Self-Review

### Spec Coverage

- Course-first platform: covered by Tasks 2, 3, 7, and 8.
- Student course/chapter loop: covered by Task 8.
- Teacher upload/review/publish loop: covered by Tasks 4, 5, and 10.
- MiroFish-style graph: covered by Task 9.
- Cited AI tutor: covered by Task 6 and Task 8.
- Seeded AI and brain/cognitive science courses: covered by Task 2.
- Vue + Flask architecture: covered by Tasks 1 and 7.
- Excluded LMS features: not implemented, intentionally omitted.

### Known Deliberate Simplifications

- Tutor retrieval is deterministic in MVP. It should later be replaced with vector search plus LLM synthesis while preserving the same API contract.
- Material parsing starts with text-like files. PDF/PPT parsing can be added behind `MaterialService.extract_text`.
- Graph persistence uses relational tables. A graph database can be introduced later without changing the frontend graph shape.

### Plan Integrity

- No task relies on Moodle/Open edX/Frappe.
- No task requires MiroFish multi-agent simulation.
- Each task has a commit boundary.
- Each backend behavior has at least one pytest or smoke verification step.
- Each frontend milestone has a build verification step.
