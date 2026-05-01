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
