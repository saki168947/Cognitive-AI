from app.services.seed_data import seed_courses
from app.services.tutor_service import TutorService


def test_tutor_answer_cites_attention_evidence_for_known_question(app):
    with app.app_context():
        seed_courses()

        result = TutorService.answer(
            "How are transformer attention and human attention related?",
            course_id="ai-intro",
        )

    assert result["insufficient_evidence"] is False
    assert "attention" in result["answer"].lower()
    assert result["citations"]
    assert any(citation["type"] == "graph_edge" for citation in result["citations"])


def test_tutor_answer_reports_insufficient_evidence_for_unknown_policy_question(app):
    with app.app_context():
        seed_courses()

        result = TutorService.answer(
            "What is the tuition refund policy?",
            course_id="ai-intro",
        )

    assert result["insufficient_evidence"] is True
    assert result["citations"] == []


def test_tutor_api_returns_answer_for_valid_question(client, app):
    with app.app_context():
        seed_courses()

    res = client.post(
        "/api/tutor/ask",
        json={
            "question": "How are transformer attention and human attention related?",
            "course_id": "ai-intro",
        },
    )
    payload = res.get_json()

    assert res.status_code == 200
    assert payload["success"] is True
    assert payload["data"]["insufficient_evidence"] is False
    assert payload["data"]["citations"]


def test_tutor_api_rejects_empty_question(client):
    res = client.post("/api/tutor/ask", json={"question": "   ", "course_id": "ai-intro"})
    payload = res.get_json()

    assert res.status_code == 400
    assert payload == {"success": False, "error": "question is required"}
