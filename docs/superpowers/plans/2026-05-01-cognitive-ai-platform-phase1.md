# Cognitive AI Platform Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert the current MVP from a course text viewer into an operational course workspace with typed learning activities.

**Architecture:** Keep Vue 3 + Flask. Add `LearningActivity` as the central backend entity, expose activity APIs, seed realistic activities, and refactor the frontend so dashboard, course pages, and teacher studio use activities instead of treating chapters as the whole product.

**Tech Stack:** Flask, SQLAlchemy, SQLite, pytest, Vue 3, Vue Router, Vitest, existing CSS/Vue component patterns.

---

## Scope

This plan implements Phase 1 from `docs/superpowers/specs/2026-05-01-cognitive-ai-platform-v2-redesign.md`.

Included:

- Remove course selection from global top navigation.
- Add typed `LearningActivity` backend model and API.
- Seed lecture, code lab, cognitive experiment, and BCI/neuro data activities for both courses.
- Make dashboard operational: next activities, active courses, teacher publish queue.
- Make course workspace activity-first: overview, modules, lectures, labs, experiments, graph, tutor, materials.
- Let Teacher Studio create a typed activity release record.

Not included:

- Real JupyterLite/Thebe execution.
- Real jsPsych execution.
- Real BrainFlow hardware stream.
- Open edX/Moodle integration.
- MirrorFish/EDUFISH code import.

## File Structure

Backend:

- Modify `backend/app/models.py`: add `LearningActivity`.
- Create `backend/app/services/activity_service.py`: activity serialization, listing, creation, dashboard summaries.
- Create `backend/app/api/activities.py`: activity endpoints.
- Modify `backend/app/api/__init__.py`: register activity API.
- Modify `backend/app/services/seed_data.py`: seed typed activities.
- Modify `backend/app/services/course_service.py`: include activity counts and course modules in details.
- Create `backend/app/tests/test_activities_api.py`: API coverage.
- Modify `backend/app/tests/test_seed_data.py`: assert seeded activities exist.
- Modify `backend/app/tests/test_courses_api.py`: assert course detail includes activities summary.

Frontend:

- Create `frontend/src/api/activities.js`: activity API wrappers.
- Create `frontend/src/views/activityState.js`: grouping, filtering, status labels.
- Create `frontend/src/components/ActivityCard.vue`: shared activity card.
- Create `frontend/src/components/ActivityTimeline.vue`: typed activity list.
- Modify `frontend/src/api/dashboard.js`: include activity summary.
- Modify `frontend/src/components/AppShell.vue`: remove course dropdown; add stable product nav.
- Modify `frontend/src/views/DashboardView.vue`: replace marketing layout with operational workspace sections.
- Modify `frontend/src/views/CourseView.vue`: add course workspace tabs and activity sections.
- Modify `frontend/src/views/TeacherStudioView.vue`: add activity creation form.
- Create `frontend/src/api/activities.test.js`: API wrapper and state tests.
- Modify `frontend/src/api/course-workspace.test.js`: course activity loading tests.
- Modify `frontend/src/api/teacher-studio.test.js`: activity creation test.

Docs:

- Modify `README.md`: mention Phase 1 activity model and run commands.

## Data Contract

`LearningActivity` fields:

```python
id: str
course_id: str
chapter_id: str | None
title: str
activity_type: str
summary: str
status: str
provider: str
launch_url: str
config_json: str
linked_concept_ids_json: str
estimated_minutes: int
release_at: datetime | None
created_at: datetime
```

Allowed `activity_type` values:

```text
reading
lecture_deck
code_lab
notebook_lab
cognitive_experiment
bci_dataset_lab
graph_task
quiz
assignment
reflection
```

Allowed `status` values:

```text
draft
scheduled
published
archived
```

Serialized activity shape:

```json
{
  "id": "activity-ai-search-lab",
  "course_id": "ai-intro",
  "chapter_id": "ai-search",
  "title": "Heuristic Search Lab",
  "type": "code_lab",
  "summary": "Experiment with heuristic search tradeoffs.",
  "status": "published",
  "provider": "jupyterlite",
  "launch_url": "",
  "config": {
    "runtime": "python",
    "entry": "astar-demo.ipynb"
  },
  "linked_concept_ids": ["concept-search"],
  "estimated_minutes": 35,
  "release_at": null,
  "created_at": "2026-05-01T00:00:00+00:00"
}
```

---

### Task 1: Backend Learning Activity Model And Service

**Files:**
- Modify: `backend/app/models.py`
- Create: `backend/app/services/activity_service.py`
- Create: `backend/app/tests/test_activities_api.py`

- [ ] **Step 1: Write failing service tests**

Create `backend/app/tests/test_activities_api.py`:

```python
from app.db import db
from app.models import LearningActivity
from app.services.activity_service import ActivityService
from app.services.seed_data import seed_courses


def test_activity_service_serializes_json_fields(app):
    with app.app_context():
        seed_courses()
        activity = LearningActivity(
            id="activity-test",
            course_id="ai-intro",
            chapter_id="ai-search",
            title="A* Search Notebook",
            activity_type="code_lab",
            summary="Run a small heuristic search notebook.",
            status="published",
            provider="jupyterlite",
            launch_url="",
            config_json='{"runtime":"python"}',
            linked_concept_ids_json='["concept-search"]',
            estimated_minutes=25,
        )
        db.session.add(activity)
        db.session.commit()

        serialized = ActivityService.serialize(activity)

    assert serialized["id"] == "activity-test"
    assert serialized["type"] == "code_lab"
    assert serialized["config"] == {"runtime": "python"}
    assert serialized["linked_concept_ids"] == ["concept-search"]
```

- [ ] **Step 2: Run the failing test**

Run:

```bash
cd backend
uv run pytest app/tests/test_activities_api.py::test_activity_service_serializes_json_fields -q
```

Expected: fail because `LearningActivity` or `ActivityService` does not exist.

- [ ] **Step 3: Add `LearningActivity` model**

Modify `backend/app/models.py` by adding this class after `Chapter`:

```python
class LearningActivity(db.Model):
    id = db.Column(db.String, primary_key=True)
    course_id = db.Column(db.String, db.ForeignKey("course.id"), nullable=False)
    chapter_id = db.Column(db.String, db.ForeignKey("chapter.id"), nullable=True)
    title = db.Column(db.String, nullable=False)
    activity_type = db.Column(db.String, nullable=False, default="reading")
    summary = db.Column(db.Text, nullable=False, default="")
    status = db.Column(db.String, nullable=False, default="draft")
    provider = db.Column(db.String, nullable=False, default="manual")
    launch_url = db.Column(db.Text, nullable=False, default="")
    config_json = db.Column(db.Text, nullable=False, default="{}")
    linked_concept_ids_json = db.Column(db.Text, nullable=False, default="[]")
    estimated_minutes = db.Column(db.Integer, nullable=False, default=20)
    release_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)
    course = db.relationship("Course", backref=db.backref("activities", lazy=True))
    chapter = db.relationship("Chapter", backref=db.backref("activities", lazy=True))
```

- [ ] **Step 4: Add activity service**

Create `backend/app/services/activity_service.py`:

```python
import json
from datetime import datetime

from app.db import db
from app.models import Chapter, Course, LearningActivity


ALLOWED_ACTIVITY_TYPES = {
    "reading",
    "lecture_deck",
    "code_lab",
    "notebook_lab",
    "cognitive_experiment",
    "bci_dataset_lab",
    "graph_task",
    "quiz",
    "assignment",
    "reflection",
}

ALLOWED_STATUSES = {"draft", "scheduled", "published", "archived"}


def _json_loads(value, fallback):
    try:
        parsed = json.loads(value or "")
    except json.JSONDecodeError:
        return fallback
    return parsed if isinstance(parsed, type(fallback)) else fallback


def _iso_or_none(value):
    if value is None:
        return None
    return value.isoformat()


class ActivityService:
    @staticmethod
    def serialize(activity):
        return {
            "id": activity.id,
            "course_id": activity.course_id,
            "chapter_id": activity.chapter_id,
            "title": activity.title,
            "type": activity.activity_type,
            "summary": activity.summary,
            "status": activity.status,
            "provider": activity.provider,
            "launch_url": activity.launch_url,
            "config": _json_loads(activity.config_json, {}),
            "linked_concept_ids": _json_loads(activity.linked_concept_ids_json, []),
            "estimated_minutes": activity.estimated_minutes,
            "release_at": _iso_or_none(activity.release_at),
            "created_at": _iso_or_none(activity.created_at),
        }

    @staticmethod
    def list_activities(course_id=None, status=None):
        query = LearningActivity.query
        if course_id:
            query = query.filter_by(course_id=course_id)
        if status:
            query = query.filter_by(status=status)
        return query.order_by(LearningActivity.created_at.desc(), LearningActivity.title.asc()).all()

    @staticmethod
    def list_for_course(course_id):
        db.get_or_404(Course, course_id)
        return ActivityService.list_activities(course_id=course_id)

    @staticmethod
    def create_activity(data):
        course_id = _required_string(data, "course_id")
        course = db.get_or_404(Course, course_id)
        chapter_id = _optional_string(data, "chapter_id")
        if chapter_id:
            chapter = db.get_or_404(Chapter, chapter_id)
            if chapter.course_id != course.id:
                raise ValueError("chapter_id must belong to course_id.")

        activity_type = _optional_string(data, "type") or "reading"
        if activity_type not in ALLOWED_ACTIVITY_TYPES:
            raise ValueError("type is not supported.")

        status = _optional_string(data, "status") or "draft"
        if status not in ALLOWED_STATUSES:
            raise ValueError("status is not supported.")

        activity_id = _required_string(data, "id")
        activity = LearningActivity(
            id=activity_id,
            course_id=course.id,
            chapter_id=chapter_id,
            title=_required_string(data, "title"),
            activity_type=activity_type,
            summary=_optional_string(data, "summary"),
            status=status,
            provider=_optional_string(data, "provider") or "manual",
            launch_url=_optional_string(data, "launch_url"),
            config_json=json.dumps(data.get("config") or {}, ensure_ascii=False),
            linked_concept_ids_json=json.dumps(data.get("linked_concept_ids") or [], ensure_ascii=False),
            estimated_minutes=int(data.get("estimated_minutes") or 20),
        )
        db.session.add(activity)
        db.session.commit()
        return activity

    @staticmethod
    def dashboard_summary():
        activities = ActivityService.list_activities()
        published = [a for a in activities if a.status == "published"]
        drafts = [a for a in activities if a.status in {"draft", "scheduled"}]
        return {
            "total": len(activities),
            "published": len(published),
            "drafts": len(drafts),
            "recent": [ActivityService.serialize(a) for a in activities[:6]],
            "next": [ActivityService.serialize(a) for a in published[:6]],
        }


def _required_string(data, key):
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} is required.")
    return value.strip()


def _optional_string(data, key):
    value = data.get(key)
    if value is None:
        return ""
    if not isinstance(value, str):
        raise ValueError(f"{key} must be a string.")
    return value.strip()
```

- [ ] **Step 5: Run service test**

Run:

```bash
cd backend
uv run pytest app/tests/test_activities_api.py::test_activity_service_serializes_json_fields -q
```

Expected: pass.

- [ ] **Step 6: Commit**

Run:

```bash
git add backend/app/models.py backend/app/services/activity_service.py backend/app/tests/test_activities_api.py
git commit -m "feat: add learning activity model"
```

---

### Task 2: Backend Activity API And Seed Data

**Files:**
- Modify: `backend/app/api/__init__.py`
- Create: `backend/app/api/activities.py`
- Modify: `backend/app/services/seed_data.py`
- Modify: `backend/app/services/course_service.py`
- Modify: `backend/app/tests/test_activities_api.py`
- Modify: `backend/app/tests/test_courses_api.py`
- Modify: `backend/app/tests/test_seed_data.py`

- [ ] **Step 1: Add failing API tests**

Append to `backend/app/tests/test_activities_api.py`:

```python
def test_list_activities_auto_seeds(client):
    res = client.get("/api/activities")
    payload = res.get_json()

    assert res.status_code == 200
    assert payload["success"] is True
    assert len(payload["data"]) >= 4
    assert {item["type"] for item in payload["data"]} >= {"lecture_deck", "code_lab", "cognitive_experiment", "bci_dataset_lab"}


def test_list_course_activities_filters_by_course(client, app):
    with app.app_context():
        seed_courses()

    res = client.get("/api/courses/ai-intro/activities")
    payload = res.get_json()

    assert res.status_code == 200
    assert payload["success"] is True
    assert payload["data"]
    assert all(item["course_id"] == "ai-intro" for item in payload["data"])


def test_create_activity_validates_and_returns_created_item(client, app):
    with app.app_context():
        seed_courses()

    res = client.post("/api/activities", json={
        "id": "activity-ai-extra-reflection",
        "course_id": "ai-intro",
        "chapter_id": "ai-search",
        "title": "Search Strategy Reflection",
        "type": "reflection",
        "summary": "Compare breadth-first search and A* on one concrete problem.",
        "status": "draft",
        "provider": "manual",
        "estimated_minutes": 15,
        "linked_concept_ids": ["concept-search"],
    })
    payload = res.get_json()

    assert res.status_code == 201
    assert payload["success"] is True
    assert payload["data"]["id"] == "activity-ai-extra-reflection"
    assert payload["data"]["type"] == "reflection"


def test_create_activity_rejects_unknown_type(client, app):
    with app.app_context():
        seed_courses()

    res = client.post("/api/activities", json={
        "id": "activity-bad",
        "course_id": "ai-intro",
        "title": "Bad Activity",
        "type": "unknown_kind",
    })
    payload = res.get_json()

    assert res.status_code == 400
    assert payload["success"] is False
    assert "type" in payload["error"]
```

Append to `backend/app/tests/test_courses_api.py`:

```python
def test_get_course_detail_includes_activity_summary(client, app):
    with app.app_context():
        seed_courses()

    res = client.get("/api/courses/ai-intro")
    payload = res.get_json()

    assert res.status_code == 200
    assert payload["data"]["activity_summary"]["total"] >= 2
    assert "code_lab" in payload["data"]["activity_summary"]["types"]
```

- [ ] **Step 2: Run failing tests**

Run:

```bash
cd backend
uv run pytest app/tests/test_activities_api.py app/tests/test_courses_api.py::test_get_course_detail_includes_activity_summary -q
```

Expected: fail because the API and seeded activities are not implemented.

- [ ] **Step 3: Add activity API**

Create `backend/app/api/activities.py`:

```python
from flask import jsonify, request

from app.api import api_bp
from app.services.activity_service import ActivityService
from app.services.seed_data import seed_courses


def _ensure_seeded():
    if not ActivityService.list_activities():
        seed_courses()


@api_bp.get("/activities")
def list_activities():
    _ensure_seeded()
    course_id = request.args.get("course_id")
    status = request.args.get("status")
    activities = ActivityService.list_activities(course_id=course_id, status=status)
    return jsonify({
        "success": True,
        "data": [ActivityService.serialize(activity) for activity in activities],
    })


@api_bp.get("/courses/<course_id>/activities")
def list_course_activities(course_id):
    _ensure_seeded()
    activities = ActivityService.list_for_course(course_id)
    return jsonify({
        "success": True,
        "data": [ActivityService.serialize(activity) for activity in activities],
    })


@api_bp.post("/activities")
def create_activity():
    try:
        activity = ActivityService.create_activity(request.get_json(silent=True) or {})
    except ValueError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400

    return jsonify({"success": True, "data": ActivityService.serialize(activity)}), 201
```

Modify `backend/app/api/__init__.py`:

```python
from . import activities  # noqa: E402,F401
```

Add that import beside the existing API module imports.

- [ ] **Step 4: Seed realistic Phase 1 activities**

Modify `backend/app/services/seed_data.py`.

Add import:

```python
from app.models import Chapter, Concept, Course, GraphEdge, LearningActivity, QuizItem
```

Add this block before quiz items:

```python
    activities = [
        LearningActivity(
            id="activity-ai-search-deck",
            course_id="ai-intro",
            chapter_id="ai-search",
            title="Lecture Deck: Search and Problem Solving",
            activity_type="lecture_deck",
            summary="A teacher-published deck introducing state spaces, uninformed search, and heuristics.",
            status="published",
            provider="slidev",
            config_json='{"format":"markdown","entry":"ai/search-and-problem-solving.md"}',
            linked_concept_ids_json='["concept-search"]',
            estimated_minutes=30,
        ),
        LearningActivity(
            id="activity-ai-search-lab",
            course_id="ai-intro",
            chapter_id="ai-search",
            title="Code Lab: Heuristic Search Sandbox",
            activity_type="code_lab",
            summary="Run and compare heuristic search strategies on a small pathfinding problem.",
            status="published",
            provider="jupyterlite",
            config_json='{"runtime":"python","entry":"labs/heuristic-search.ipynb"}',
            linked_concept_ids_json='["concept-search"]',
            estimated_minutes=40,
        ),
        LearningActivity(
            id="activity-brain-attention-deck",
            course_id="brain-cog-intro",
            chapter_id="brain-attention",
            title="Lecture Deck: Attention and Cognitive Control",
            activity_type="lecture_deck",
            summary="A teacher-published deck connecting selective attention, working memory, and control.",
            status="published",
            provider="revealjs",
            config_json='{"format":"markdown","entry":"brain/attention-control.md"}',
            linked_concept_ids_json='["concept-human-attention"]',
            estimated_minutes=30,
        ),
        LearningActivity(
            id="activity-brain-stroop",
            course_id="brain-cog-intro",
            chapter_id="brain-attention",
            title="Cognitive Experiment: Stroop Task",
            activity_type="cognitive_experiment",
            summary="Measure reaction time and interference in a browser-based attention experiment.",
            status="published",
            provider="jspsych",
            config_json='{"experiment":"stroop","trials":24}',
            linked_concept_ids_json='["concept-human-attention"]',
            estimated_minutes=20,
        ),
        LearningActivity(
            id="activity-brain-eeg-demo",
            course_id="brain-cog-intro",
            chapter_id="brain-attention",
            title="Neuro Data Lab: EEG Attention Demo",
            activity_type="bci_dataset_lab",
            summary="Inspect sample EEG-like signals and connect event-related changes to attention.",
            status="draft",
            provider="mne-python",
            config_json='{"dataset":"sample-eeg-attention","entry":"labs/eeg-attention-demo.ipynb"}',
            linked_concept_ids_json='["concept-human-attention"]',
            estimated_minutes=45,
        ),
    ]
    _merge_all(activities)
```

- [ ] **Step 5: Add activity summary to course detail**

Modify `backend/app/services/course_service.py`.

Add import:

```python
from app.models import Chapter, Concept, Course, GraphEdge, LearningActivity, QuizItem
```

In `get_course_detail`, query activities:

```python
        activities = LearningActivity.query.filter_by(course_id=course_id).all()
        activity_types = {}
        for activity in activities:
            activity_types[activity.activity_type] = activity_types.get(activity.activity_type, 0) + 1
```

Add this key to the returned dict:

```python
            "activity_summary": {
                "total": len(activities),
                "published": len([a for a in activities if a.status == "published"]),
                "drafts": len([a for a in activities if a.status in {"draft", "scheduled"}]),
                "types": activity_types,
            },
```

- [ ] **Step 6: Run backend tests**

Run:

```bash
cd backend
uv run pytest -q
```

Expected: all backend tests pass.

- [ ] **Step 7: Commit**

Run:

```bash
git add backend/app/api/__init__.py backend/app/api/activities.py backend/app/services/seed_data.py backend/app/services/course_service.py backend/app/tests/test_activities_api.py backend/app/tests/test_courses_api.py backend/app/tests/test_seed_data.py
git commit -m "feat: add activity api and seed data"
```

---

### Task 3: Frontend Activity API And State Helpers

**Files:**
- Create: `frontend/src/api/activities.js`
- Create: `frontend/src/views/activityState.js`
- Create: `frontend/src/api/activities.test.js`
- Modify: `frontend/src/api/course-workspace.test.js`

- [ ] **Step 1: Add failing frontend tests**

Create `frontend/src/api/activities.test.js`:

```javascript
import { beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('./client', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn()
  }
}));

const { default: apiClient } = await import('./client');
const { listActivities, listCourseActivities, createActivity } = await import('./activities');
const {
  activityTypeLabel,
  groupActivitiesByType,
  publishedActivities,
  nextPublishedActivity
} = await import('../views/activityState');

describe('activity API wrappers', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('loads all activities and course-scoped activities', async () => {
    apiClient.get.mockResolvedValueOnce([{ id: 'activity-1' }]);
    apiClient.get.mockResolvedValueOnce([{ id: 'activity-2' }]);

    await expect(listActivities()).resolves.toEqual([{ id: 'activity-1' }]);
    await expect(listCourseActivities('ai-intro')).resolves.toEqual([{ id: 'activity-2' }]);

    expect(apiClient.get).toHaveBeenNthCalledWith(1, '/api/activities', { params: {} });
    expect(apiClient.get).toHaveBeenNthCalledWith(2, '/api/courses/ai-intro/activities');
  });

  it('creates activities through the shared api client', async () => {
    const payload = { id: 'activity-new', course_id: 'ai-intro', title: 'New Activity', type: 'reflection' };
    apiClient.post.mockResolvedValue({ id: 'activity-new' });

    await expect(createActivity(payload)).resolves.toEqual({ id: 'activity-new' });

    expect(apiClient.post).toHaveBeenCalledWith('/api/activities', payload);
  });
});

describe('activity state helpers', () => {
  const activities = [
    { id: 'draft', type: 'lecture_deck', status: 'draft' },
    { id: 'lab', type: 'code_lab', status: 'published' },
    { id: 'experiment', type: 'cognitive_experiment', status: 'published' }
  ];

  it('labels and groups activities', () => {
    expect(activityTypeLabel('code_lab')).toBe('代码实验');
    expect(groupActivitiesByType(activities).code_lab[0].id).toBe('lab');
  });

  it('finds published activities and the next published item', () => {
    expect(publishedActivities(activities).map((item) => item.id)).toEqual(['lab', 'experiment']);
    expect(nextPublishedActivity(activities).id).toBe('lab');
  });
});
```

- [ ] **Step 2: Run failing frontend test**

Run:

```bash
cd frontend
npm test -- activities.test.js
```

Expected: fail because files do not exist.

- [ ] **Step 3: Add activity API wrapper**

Create `frontend/src/api/activities.js`:

```javascript
import apiClient from './client';

export function listActivities(params = {}) {
  return apiClient.get('/api/activities', { params });
}

export function listCourseActivities(courseId) {
  return apiClient.get(`/api/courses/${courseId}/activities`);
}

export function createActivity(payload) {
  return apiClient.post('/api/activities', payload);
}
```

- [ ] **Step 4: Add activity state helpers**

Create `frontend/src/views/activityState.js`:

```javascript
export const ACTIVITY_TYPE_LABELS = {
  reading: '阅读',
  lecture_deck: '课件',
  h5p_activity: '互动内容',
  code_lab: '代码实验',
  notebook_lab: 'Notebook 实验',
  cognitive_experiment: '认知实验',
  bci_dataset_lab: '脑机数据实验',
  graph_task: '图谱任务',
  quiz: '测验',
  assignment: '作业',
  reflection: '反思'
};

export function activityTypeLabel(type) {
  return ACTIVITY_TYPE_LABELS[type] || '活动';
}

export function safeActivities(value) {
  return Array.isArray(value) ? value : [];
}

export function groupActivitiesByType(activities) {
  return safeActivities(activities).reduce((groups, activity) => {
    const type = activity?.type || 'reading';
    return {
      ...groups,
      [type]: [...(groups[type] || []), activity]
    };
  }, {});
}

export function publishedActivities(activities) {
  return safeActivities(activities).filter((activity) => activity.status === 'published');
}

export function draftActivities(activities) {
  return safeActivities(activities).filter((activity) =>
    activity.status === 'draft' || activity.status === 'scheduled'
  );
}

export function nextPublishedActivity(activities) {
  return publishedActivities(activities)[0] || null;
}
```

- [ ] **Step 5: Run frontend test**

Run:

```bash
cd frontend
npm test -- activities.test.js
```

Expected: pass.

- [ ] **Step 6: Commit**

Run:

```bash
git add frontend/src/api/activities.js frontend/src/views/activityState.js frontend/src/api/activities.test.js
git commit -m "feat: add frontend activity api helpers"
```

---

### Task 4: Global Shell And Operational Dashboard

**Files:**
- Modify: `frontend/src/components/AppShell.vue`
- Modify: `frontend/src/api/dashboard.js`
- Modify: `frontend/src/views/DashboardView.vue`
- Create: `frontend/src/components/ActivityCard.vue`
- Create: `frontend/src/components/ActivityTimeline.vue`
- Modify: `frontend/src/api/activities.test.js`

- [ ] **Step 1: Add dashboard summary test**

Append to `frontend/src/api/activities.test.js`:

```javascript
const { getDashboardSummary } = await import('./dashboard');

describe('dashboard summary', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('includes activity totals from the activities API', async () => {
    apiClient.get.mockResolvedValueOnce([{ id: 'ai-intro', title: 'AI', chapters: [] }]);
    apiClient.get.mockResolvedValueOnce([]);
    apiClient.get.mockResolvedValueOnce([
      { id: 'activity-1', status: 'published', type: 'code_lab' },
      { id: 'activity-2', status: 'draft', type: 'lecture_deck' }
    ]);
    apiClient.get.mockResolvedValueOnce({ nodes: [], edges: [] });

    const summary = await getDashboardSummary();

    expect(summary.totals.activities).toBe(2);
    expect(summary.totals.publishedActivities).toBe(1);
    expect(summary.totals.draftActivities).toBe(1);
    expect(summary.nextActivities[0].id).toBe('activity-1');
  });
});
```

- [ ] **Step 2: Run failing dashboard test**

Run:

```bash
cd frontend
npm test -- activities.test.js
```

Expected: fail because dashboard does not load activities.

- [ ] **Step 3: Update dashboard API aggregation**

Modify `frontend/src/api/dashboard.js`:

```javascript
import { listActivities } from './activities';
import { listCourses } from './courses';
import { getGraph } from './graph';
import { listReviewItems } from './review';
import { draftActivities, publishedActivities } from '../views/activityState';
```

Change the first `Promise.allSettled` call to include `listActivities()`:

```javascript
  const [coursesResult, reviewItemsResult, activitiesResult] = await Promise.allSettled([
    listCourses(),
    listReviewItems(),
    listActivities()
  ]);
```

Add:

```javascript
  const activities = activitiesResult.status === 'fulfilled' ? safeArray(activitiesResult.value) : [];
  const published = publishedActivities(activities);
  const drafts = draftActivities(activities);
```

Add totals:

```javascript
      activities: activities.length,
      publishedActivities: published.length,
      draftActivities: drafts.length,
```

Add return fields:

```javascript
    activities,
    nextActivities: published.slice(0, 6),
    draftActivities: drafts.slice(0, 6),
```

- [ ] **Step 4: Create shared activity components**

Create `frontend/src/components/ActivityCard.vue`:

```vue
<template>
  <article class="activity-card" :data-type="activity.type">
    <div class="activity-card-head">
      <span class="activity-type">{{ activityTypeLabel(activity.type) }}</span>
      <span class="activity-status">{{ activity.status || 'draft' }}</span>
    </div>
    <h3>{{ activity.title }}</h3>
    <p>{{ activity.summary }}</p>
    <dl class="activity-meta">
      <div>
        <dt>工具</dt>
        <dd>{{ activity.provider || 'manual' }}</dd>
      </div>
      <div>
        <dt>时间</dt>
        <dd>{{ activity.estimated_minutes || 20 }} 分钟</dd>
      </div>
    </dl>
  </article>
</template>

<script setup>
import { activityTypeLabel } from '../views/activityState';

defineProps({
  activity: {
    type: Object,
    required: true
  }
});
</script>
```

Create `frontend/src/components/ActivityTimeline.vue`:

```vue
<template>
  <section class="activity-timeline">
    <ActivityCard
      v-for="activity in activities"
      :key="activity.id"
      :activity="activity"
    />
    <p v-if="activities.length === 0" class="status-message">{{ emptyText }}</p>
  </section>
</template>

<script setup>
import ActivityCard from './ActivityCard.vue';

defineProps({
  activities: {
    type: Array,
    default: () => []
  },
  emptyText: {
    type: String,
    default: '暂无活动。'
  }
});
</script>
```

- [ ] **Step 5: Refactor AppShell global nav**

Modify `frontend/src/components/AppShell.vue`:

- Remove `listCourses`, `courses`, `courseMenuOpen`, `activeCourse`, `toggleCourseMenu`, `closeCourseMenu`.
- Replace `navLinks` with:

```javascript
const navLinks = [
  { to: '/', label: '工作台', match: (r) => r.name === 'dashboard' },
  { to: '/courses/ai-intro', label: '课程工作区', match: (r) => r.name === 'course' },
  { to: '/teacher', label: '教师工作室', match: (r) => r.name === 'teacher' }
];
```

- Delete the `course-switcher` block from the template.

Expected behavior:

The global top nav no longer contains a course dropdown. Course selection happens in dashboard and course workspace content.

- [ ] **Step 6: Replace dashboard with operational sections**

Modify `frontend/src/views/DashboardView.vue` so the first viewport contains:

- title: `课程工作台`
- primary action to first next activity's course
- stats for courses, activities, pending reviews, graph concepts
- `ActivityTimeline` for `nextActivities`
- course cards with activity counts
- teacher draft/review queue summary

Use current dark visual tokens if keeping `AppShell`; avoid a marketing hero headline as the main product structure.

Minimum script state:

```javascript
const nextActivities = computed(() => summary.value?.nextActivities ?? []);
const draftActivities = computed(() => summary.value?.draftActivities ?? []);
```

Minimum template behavior:

```vue
<ActivityTimeline
  :activities="nextActivities"
  empty-text="暂无已发布活动。请到教师工作室发布课件、实验或代码训练。"
/>
```

- [ ] **Step 7: Run frontend tests and build**

Run:

```bash
cd frontend
npm test -- activities.test.js
npm run build
```

Expected: tests pass and Vite build succeeds.

- [ ] **Step 8: Commit**

Run:

```bash
git add frontend/src/components/AppShell.vue frontend/src/api/dashboard.js frontend/src/views/DashboardView.vue frontend/src/components/ActivityCard.vue frontend/src/components/ActivityTimeline.vue frontend/src/api/activities.test.js
git commit -m "feat: make dashboard activity driven"
```

---

### Task 5: Course Workspace Tabs And Activity Sections

**Files:**
- Modify: `frontend/src/views/CourseView.vue`
- Modify: `frontend/src/api/course-workspace.test.js`

- [ ] **Step 1: Extend course workspace API test**

Modify `frontend/src/api/course-workspace.test.js`.

Add `listCourseActivities` import:

```javascript
const { listCourseActivities } = await import('./activities');
```

Add this test:

```javascript
it('loads course-scoped learning activities', async () => {
  apiClient.get.mockResolvedValue([{ id: 'activity-ai-search-lab', type: 'code_lab' }]);

  await expect(listCourseActivities('ai-intro')).resolves.toEqual([
    { id: 'activity-ai-search-lab', type: 'code_lab' }
  ]);

  expect(apiClient.get).toHaveBeenCalledWith('/api/courses/ai-intro/activities');
});
```

- [ ] **Step 2: Run frontend test**

Run:

```bash
cd frontend
npm test -- course-workspace.test.js
```

Expected: pass after Task 3.

- [ ] **Step 3: Load activities in `CourseView.vue`**

Modify imports:

```javascript
import { listCourseActivities } from '../api/activities';
import ActivityTimeline from '../components/ActivityTimeline.vue';
import { groupActivitiesByType } from './activityState';
```

Add refs:

```javascript
const activities = ref([]);
const activitiesLoading = ref(false);
const activitiesError = ref('');
const activeSection = ref('overview');
```

Add computed groups:

```javascript
const activityGroups = computed(() => groupActivitiesByType(activities.value));
const lectures = computed(() => activityGroups.value.lecture_deck || []);
const labs = computed(() => [
  ...(activityGroups.value.code_lab || []),
  ...(activityGroups.value.notebook_lab || [])
]);
const experiments = computed(() => [
  ...(activityGroups.value.cognitive_experiment || []),
  ...(activityGroups.value.bci_dataset_lab || [])
]);
```

In `loadCourse`, include `listCourseActivities(props.courseId)` in `Promise.allSettled`.

Set `activities.value` from the fulfilled result, and set `activitiesError` on rejection.

- [ ] **Step 4: Add course workspace navigation**

In the template, replace the plain two-column course content with a course workspace header and section buttons:

```vue
<nav class="course-tabs" aria-label="课程工作区">
  <button type="button" :data-active="activeSection === 'overview'" @click="activeSection = 'overview'">概览</button>
  <button type="button" :data-active="activeSection === 'lectures'" @click="activeSection = 'lectures'">课件</button>
  <button type="button" :data-active="activeSection === 'labs'" @click="activeSection = 'labs'">代码训练</button>
  <button type="button" :data-active="activeSection === 'experiments'" @click="activeSection = 'experiments'">认知 / 脑机实验</button>
  <button type="button" :data-active="activeSection === 'graph'" @click="activeSection = 'graph'">知识图谱</button>
  <button type="button" :data-active="activeSection === 'tutor'" @click="activeSection = 'tutor'">AI 导师</button>
</nav>
```

Render activity sections:

```vue
<ActivityTimeline
  v-if="activeSection === 'lectures'"
  :activities="lectures"
  empty-text="暂无已发布课件。"
/>
<ActivityTimeline
  v-if="activeSection === 'labs'"
  :activities="labs"
  empty-text="暂无代码训练或 Notebook 实验。"
/>
<ActivityTimeline
  v-if="activeSection === 'experiments'"
  :activities="experiments"
  empty-text="暂无认知实验或脑机数据实验。"
/>
```

Keep `ChapterWorkspace`, `AITutorPanel`, and `GraphPanel`, but make them section-specific instead of one long stack.

- [ ] **Step 5: Run frontend build**

Run:

```bash
cd frontend
npm test -- course-workspace.test.js
npm run build
```

Expected: tests pass and build succeeds.

- [ ] **Step 6: Commit**

Run:

```bash
git add frontend/src/views/CourseView.vue frontend/src/api/course-workspace.test.js
git commit -m "feat: add course workspace activity sections"
```

---

### Task 6: Teacher Studio Activity Publishing

**Files:**
- Modify: `frontend/src/views/TeacherStudioView.vue`
- Modify: `frontend/src/api/teacher-studio.test.js`

- [ ] **Step 1: Add frontend activity creation test**

Modify `frontend/src/api/teacher-studio.test.js`.

Add import:

```javascript
const { createActivity } = await import('./activities');
```

Add test:

```javascript
it('creates typed learning activities through the shared api client', async () => {
  const payload = {
    id: 'activity-teacher-created',
    course_id: 'ai-intro',
    title: 'Teacher Created Lab',
    type: 'code_lab',
    status: 'draft'
  };
  apiClient.post.mockResolvedValue({ id: 'activity-teacher-created' });

  await expect(createActivity(payload)).resolves.toEqual({ id: 'activity-teacher-created' });

  expect(apiClient.post).toHaveBeenCalledWith('/api/activities', payload);
});
```

- [ ] **Step 2: Run frontend test**

Run:

```bash
cd frontend
npm test -- teacher-studio.test.js
```

Expected: pass after Task 3.

- [ ] **Step 3: Add activity creation state to Teacher Studio**

Modify `frontend/src/views/TeacherStudioView.vue`.

Add import:

```javascript
import { createActivity } from '../api/activities';
```

Add refs:

```javascript
const activityForm = ref({
  id: '',
  title: '',
  type: 'lecture_deck',
  summary: '',
  provider: 'manual',
  estimated_minutes: 30
});
const creatingActivity = ref(false);
```

Add computed:

```javascript
const activityCreateDisabled = computed(() =>
  creatingActivity.value ||
  !selectedCourseId.value ||
  !activityForm.value.id.trim() ||
  !activityForm.value.title.trim()
);
```

Add submit function:

```javascript
async function submitActivity() {
  if (activityCreateDisabled.value) {
    return;
  }

  creatingActivity.value = true;
  error.value = '';
  message.value = '';

  try {
    const created = await createActivity({
      id: activityForm.value.id.trim(),
      course_id: selectedCourseId.value,
      title: activityForm.value.title.trim(),
      type: activityForm.value.type,
      summary: activityForm.value.summary.trim(),
      provider: activityForm.value.provider.trim() || 'manual',
      status: 'draft',
      estimated_minutes: Number(activityForm.value.estimated_minutes) || 30
    });
    message.value = `已创建活动 ${created.id}`;
    activityForm.value = {
      id: '',
      title: '',
      type: 'lecture_deck',
      summary: '',
      provider: 'manual',
      estimated_minutes: 30
    };
  } catch (caughtError) {
    error.value = caughtError?.message || '无法创建活动。';
  } finally {
    creatingActivity.value = false;
  }
}
```

- [ ] **Step 4: Add activity creation form**

Add a panel beside the material upload panel:

```vue
<section class="panel teacher-activity-panel">
  <header class="panel-header">
    <p class="eyebrow">活动</p>
    <h2>创建学习活动</h2>
  </header>

  <form class="teacher-upload-form" @submit.prevent="submitActivity">
    <label class="form-field">
      <span class="field-label">活动 ID</span>
      <input v-model="activityForm.id" class="form-control" type="text" aria-describedby="activity-id-help" />
      <small id="activity-id-help" class="field-help">例如 activity-ai-search-lab</small>
    </label>
    <label class="form-field">
      <span class="field-label">标题</span>
      <input v-model="activityForm.title" class="form-control" type="text" aria-describedby="activity-title-help" />
      <small id="activity-title-help" class="field-help">例如 Heuristic Search Lab</small>
    </label>
    <label class="form-field">
      <span class="field-label">类型</span>
      <select v-model="activityForm.type" class="form-control">
        <option value="lecture_deck">课件</option>
        <option value="code_lab">代码实验</option>
        <option value="cognitive_experiment">认知实验</option>
        <option value="bci_dataset_lab">脑机数据实验</option>
        <option value="reflection">反思</option>
      </select>
    </label>
    <label class="form-field">
      <span class="field-label">工具提供方</span>
      <input v-model="activityForm.provider" class="form-control" type="text" aria-describedby="activity-provider-help" />
      <small id="activity-provider-help" class="field-help">例如 slidev / jupyterlite / jspsych</small>
    </label>
    <label class="form-field">
      <span class="field-label">预计分钟</span>
      <input v-model.number="activityForm.estimated_minutes" class="form-control" type="number" min="5" max="180" />
    </label>
    <label class="form-field">
      <span class="field-label">摘要</span>
      <textarea v-model="activityForm.summary" class="form-control" rows="3"></textarea>
    </label>

    <button type="submit" class="button" :disabled="activityCreateDisabled">
      {{ creatingActivity ? '正在创建…' : '创建草稿活动' }}
    </button>
  </form>
</section>
```

- [ ] **Step 5: Run full verification**

Run:

```bash
cd backend
uv run pytest -q
cd ../frontend
npm test
npm run build
```

Expected: backend tests pass, frontend tests pass, build succeeds.

- [ ] **Step 6: Commit**

Run:

```bash
git add frontend/src/views/TeacherStudioView.vue frontend/src/api/teacher-studio.test.js
git commit -m "feat: add teacher activity drafts"
```

---

### Task 7: Documentation And Final Verification

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Update README**

Add a section after `## MVP`:

```markdown
## Phase 1 Platform Shape

The platform now treats learning content as typed activities:

- lecture decks
- code labs
- cognitive experiments
- BCI/neuro data labs
- graph tasks
- quizzes and reflections

Courses are workspaces that organize activities, chapters, graph context, and AI tutoring. Teacher Studio can create draft learning activities before publishing deeper integrations.
```

- [ ] **Step 2: Run final verification**

Run:

```bash
npm run test
npm run build
```

Expected:

- `npm run test` completes backend and frontend tests.
- `npm run build` completes Vite build.

- [ ] **Step 3: Inspect final git diff**

Run:

```bash
git status --short
git diff --stat
```

Expected:

- Only intended Phase 1 files are modified.
- Pre-existing unrelated user changes remain untouched.

- [ ] **Step 4: Commit documentation**

Run:

```bash
git add README.md
git commit -m "docs: describe activity based platform phase"
```

## Self-Review

Spec coverage:

- Navigation issue is covered by Task 4.
- Activity model is covered by Tasks 1 and 2.
- Operational dashboard is covered by Task 4.
- Course workspace tabs and typed sections are covered by Task 5.
- Teacher activity creation is covered by Task 6.
- Seed activities for both courses are covered by Task 2.
- Real external integrations are intentionally excluded from Phase 1 and represented as provider metadata.

Scope check:

- The plan does not implement JupyterLite, jsPsych, BrainFlow, or Open edX. It creates the activity foundation that those integrations need.
- The plan does not claim EDUFISH/MirrorFish code reuse.
- The plan avoids continuing homepage animation work before product structure is fixed.

Verification:

- Backend: `cd backend && uv run pytest -q`
- Frontend: `cd frontend && npm test && npm run build`
- Full root command: `npm run test && npm run build`
