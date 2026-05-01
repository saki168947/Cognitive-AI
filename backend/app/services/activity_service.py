import json

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
