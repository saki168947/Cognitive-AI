"""Progress event tracking and per-student aggregations."""

from __future__ import annotations

import json
from collections import Counter
from uuid import uuid4

from app.db import db
from app.models import Chapter, Course, LearningActivity, ProgressEvent, User


_ALLOWED_EVENT_TYPES = {
    "viewed",
    "started",
    "completed",
    "answered_quiz",
    "asked_tutor",
    "submitted_assignment",
    "ran_lab",
}


class ProgressService:
    @staticmethod
    def record(
        student_id: str,
        event_type: str,
        course_id: str | None = None,
        chapter_id: str | None = None,
        activity_id: str | None = None,
        payload: dict | None = None,
        commit: bool = True,
    ) -> ProgressEvent:
        student = db.session.get(User, student_id)
        if student is None:
            raise ValueError(f"student not found: {student_id}")
        if event_type not in _ALLOWED_EVENT_TYPES:
            raise ValueError(f"event_type must be one of {_ALLOWED_EVENT_TYPES}")
        if course_id is not None and db.session.get(Course, course_id) is None:
            raise ValueError(f"course not found: {course_id}")
        if chapter_id is not None and db.session.get(Chapter, chapter_id) is None:
            raise ValueError(f"chapter not found: {chapter_id}")
        if activity_id is not None and db.session.get(LearningActivity, activity_id) is None:
            raise ValueError(f"activity not found: {activity_id}")

        event = ProgressEvent(
            id=f"progress-{uuid4().hex}",
            student_id=student_id,
            course_id=course_id,
            chapter_id=chapter_id,
            activity_id=activity_id,
            event_type=event_type,
            payload_json=json.dumps(payload or {}, ensure_ascii=False),
        )
        db.session.add(event)
        if commit:
            db.session.commit()
        else:
            db.session.flush()
        db.session.refresh(event)
        return event

    @staticmethod
    def summary_for_student(student_id: str) -> dict:
        events = (
            ProgressEvent.query.filter_by(student_id=student_id)
            .order_by(ProgressEvent.created_at.desc())
            .all()
        )
        counts = Counter(e.event_type for e in events)
        completed_chapters = {e.chapter_id for e in events if e.event_type == "completed" and e.chapter_id}
        viewed_chapters = {e.chapter_id for e in events if e.event_type == "viewed" and e.chapter_id}
        completed_activities = {e.activity_id for e in events if e.event_type == "completed" and e.activity_id}

        return {
            "student_id": student_id,
            "total_events": len(events),
            "event_counts": dict(counts),
            "completed_chapters": sorted(completed_chapters),
            "viewed_chapters": sorted(viewed_chapters),
            "completed_activities": sorted(completed_activities),
            "recent_events": [
                {
                    "id": e.id,
                    "event_type": e.event_type,
                    "course_id": e.course_id,
                    "chapter_id": e.chapter_id,
                    "activity_id": e.activity_id,
                    "created_at": e.created_at.isoformat() if e.created_at else None,
                }
                for e in events[:20]
            ],
        }

    @staticmethod
    def cohort_summary(course_id: str) -> dict:
        """Aggregate progress across all students for a course (teacher view)."""
        events = (
            ProgressEvent.query.filter_by(course_id=course_id).all()
        )
        student_ids = {e.student_id for e in events}
        per_chapter_views = Counter(e.chapter_id for e in events if e.chapter_id and e.event_type == "viewed")
        per_chapter_completions = Counter(
            e.chapter_id for e in events if e.chapter_id and e.event_type == "completed"
        )
        per_event = Counter(e.event_type for e in events)

        return {
            "course_id": course_id,
            "active_students": len(student_ids),
            "total_events": len(events),
            "event_counts": dict(per_event),
            "chapter_views": dict(per_chapter_views),
            "chapter_completions": dict(per_chapter_completions),
        }
