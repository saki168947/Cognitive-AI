import pytest

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


def test_activity_service_create_activity_serializes_supported_fields(app):
    with app.app_context():
        seed_courses()

        activity = ActivityService.create_activity({
            "id": "activity-create-test",
            "course_id": "ai-intro",
            "chapter_id": "ai-search",
            "title": "Scheduled Notebook",
            "type": "notebook_lab",
            "summary": "Use a notebook to explore search.",
            "status": "scheduled",
            "provider": "jupyterlite",
            "launch_url": "https://example.test/notebook",
            "config": {"runtime": "python", "kernel": "pyodide"},
            "linked_concept_ids": ["concept-search"],
            "estimated_minutes": 35,
            "release_at": "2026-05-02T09:30:00",
        })

        serialized = ActivityService.serialize(activity)

    assert serialized["id"] == "activity-create-test"
    assert serialized["type"] == "notebook_lab"
    assert serialized["config"] == {"runtime": "python", "kernel": "pyodide"}
    assert serialized["linked_concept_ids"] == ["concept-search"]
    assert serialized["estimated_minutes"] == 35
    assert serialized["release_at"] == "2026-05-02T09:30:00"


def test_activity_service_create_activity_rejects_invalid_config(app):
    with app.app_context():
        seed_courses()

        with pytest.raises(ValueError, match="config"):
            ActivityService.create_activity({
                "id": "activity-invalid-config",
                "course_id": "ai-intro",
                "title": "Invalid Config",
                "config": ["not", "an", "object"],
            })


@pytest.mark.parametrize("linked_concept_ids", ["concept-search", ["concept-search", 42]])
def test_activity_service_create_activity_rejects_invalid_linked_concept_ids(app, linked_concept_ids):
    with app.app_context():
        seed_courses()

        with pytest.raises(ValueError, match="linked_concept_ids"):
            ActivityService.create_activity({
                "id": "activity-invalid-links",
                "course_id": "ai-intro",
                "title": "Invalid Links",
                "linked_concept_ids": linked_concept_ids,
            })


def test_activity_service_create_activity_rejects_invalid_release_at(app):
    with app.app_context():
        seed_courses()

        with pytest.raises(ValueError, match="release_at"):
            ActivityService.create_activity({
                "id": "activity-invalid-release",
                "course_id": "ai-intro",
                "title": "Invalid Release",
                "release_at": "next Tuesday",
            })


@pytest.mark.parametrize("estimated_minutes", [0, -5, "twenty", True])
def test_activity_service_create_activity_rejects_invalid_estimated_minutes(app, estimated_minutes):
    with app.app_context():
        seed_courses()

        with pytest.raises(ValueError, match="estimated_minutes"):
            ActivityService.create_activity({
                "id": "activity-invalid-estimate",
                "course_id": "ai-intro",
                "title": "Invalid Estimate",
                "estimated_minutes": estimated_minutes,
            })
