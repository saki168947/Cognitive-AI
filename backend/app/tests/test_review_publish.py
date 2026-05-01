import pytest

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
                    {
                        "id": "concept-working-memory",
                        "course_id": "brain-cog-intro",
                        "label": "Working Memory",
                        "definition": "Temporary maintenance and manipulation of information.",
                    }
                ],
                "edges": [
                    {
                        "id": "edge-working-memory-attention",
                        "course_id": "brain-cog-intro",
                        "source": "concept-working-memory",
                        "target": "concept-human-attention",
                        "relationship": "RELATED_TO",
                        "evidence": "Working memory and attention are tightly coupled.",
                    }
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


def test_review_items_endpoint_returns_json_envelope(client, app):
    with app.app_context():
        ReviewService.create_graph_suggestion(
            title="Candidate relation",
            payload={"course_id": "brain-cog-intro", "concepts": [], "edges": []},
        )

    res = client.get("/api/review/items")
    payload = res.get_json()

    assert res.status_code == 200
    assert payload["success"] is True
    assert payload["data"][0]["title"] == "Candidate relation"
    assert payload["data"][0]["payload"]["course_id"] == "brain-cog-intro"


def test_review_decision_and_publish_endpoints_update_status(client, app):
    with app.app_context():
        seed_courses()
        item = ReviewService.create_graph_suggestion(
            title="Attention alias",
            payload={
                "course_id": "brain-cog-intro",
                "concepts": [
                    {
                        "id": "concept-attention-control",
                        "label": "Attention Control",
                        "definition": "Directing limited cognitive resources toward task-relevant signals.",
                    }
                ],
                "edges": [
                    {
                        "id": "edge-attention-control-human-attention",
                        "source": "concept-attention-control",
                        "target": "concept-human-attention",
                        "relationship": "RELATED_TO",
                    }
                ],
            },
        )

    approve_res = client.post(
        f"/api/review/items/{item.id}/approve",
        json={"reviewer": "teacher", "notes": "Looks useful."},
    )
    publish_res = client.post(f"/api/review/items/{item.id}/publish")

    assert approve_res.status_code == 200
    assert approve_res.get_json()["data"]["status"] == "reviewed"
    assert publish_res.status_code == 200
    assert publish_res.get_json()["data"]["status"] == "published"


def test_review_reject_endpoint_updates_status(client, app):
    with app.app_context():
        item = ReviewService.create_graph_suggestion(
            title="Weak relation",
            payload={"course_id": "brain-cog-intro", "concepts": [], "edges": []},
        )

    res = client.post(
        f"/api/review/items/{item.id}/reject",
        json={"reviewer": "teacher", "notes": "Needs stronger evidence."},
    )
    payload = res.get_json()

    assert res.status_code == 200
    assert payload["success"] is True
    assert payload["data"]["status"] == "rejected"
    assert payload["data"]["decision_notes"] == "Needs stronger evidence."


def test_rejected_item_cannot_be_approved(client, app):
    with app.app_context():
        item = ReviewService.create_graph_suggestion(
            title="Rejected relation",
            payload={"course_id": "brain-cog-intro", "concepts": [], "edges": []},
        )
        ReviewService.reject_item(item.id, reviewer="teacher")
        item_id = item.id

    res = client.post(f"/api/review/items/{item_id}/approve", json={"reviewer": "teacher"})
    payload = res.get_json()

    assert res.status_code == 400
    assert payload == {"success": False, "error": "Only draft items can be approved."}


def test_published_item_cannot_be_rejected(client, app):
    with app.app_context():
        item = ReviewService.create_graph_suggestion(
            title="Published relation",
            payload={"course_id": "brain-cog-intro", "concepts": [], "edges": []},
        )
        ReviewService.approve_item(item.id, reviewer="teacher")
        ReviewService.publish_item(item.id)
        item_id = item.id

    res = client.post(f"/api/review/items/{item_id}/reject", json={"reviewer": "teacher"})
    payload = res.get_json()

    assert res.status_code == 400
    assert payload == {"success": False, "error": "Only draft items can be rejected."}


def test_publish_non_reviewed_item_returns_clear_api_error(client, app):
    with app.app_context():
        item = ReviewService.create_graph_suggestion(
            title="Unreviewed relation",
            payload={"course_id": "brain-cog-intro", "concepts": [], "edges": []},
        )

    res = client.post(f"/api/review/items/{item.id}/publish")
    payload = res.get_json()

    assert res.status_code == 400
    assert payload == {"success": False, "error": "Only reviewed items can be published."}


def test_publish_non_reviewed_item_raises_clear_service_error(app):
    with app.app_context():
        item = ReviewService.create_graph_suggestion(
            title="Unreviewed relation",
            payload={"course_id": "brain-cog-intro", "concepts": [], "edges": []},
        )

        with pytest.raises(ValueError, match="Only reviewed items can be published."):
            ReviewService.publish_item(item.id)


def test_failed_publish_does_not_leave_partial_concepts(app):
    with app.app_context():
        seed_courses()
        item = ReviewService.create_graph_suggestion(
            title="Invalid edge target",
            payload={
                "course_id": "brain-cog-intro",
                "concepts": [
                    {
                        "id": "concept-partial-write",
                        "label": "Partial Write",
                        "definition": "This should not persist if publish fails.",
                    }
                ],
                "edges": [
                    {
                        "id": "edge-invalid-target",
                        "source": "concept-partial-write",
                        "target": "concept-missing-target",
                        "relationship": "RELATED_TO",
                    }
                ],
            },
        )
        ReviewService.approve_item(item.id, reviewer="teacher")

        with pytest.raises(ValueError, match="Edge target concept does not exist"):
            ReviewService.publish_item(item.id)

        db.session.commit()

        assert db.session.get(Concept, "concept-partial-write") is None
        assert db.session.get(GraphEdge, "edge-invalid-target") is None


def test_publish_non_object_payload_returns_clear_api_error(client, app):
    with app.app_context():
        item = ReviewService.create_graph_suggestion(
            title="Invalid payload",
            payload=["not", "an", "object"],
        )
        ReviewService.approve_item(item.id, reviewer="teacher")
        item_id = item.id

    res = client.post(f"/api/review/items/{item_id}/publish")
    payload = res.get_json()

    assert res.status_code == 400
    assert payload == {"success": False, "error": "Review payload must be an object."}
