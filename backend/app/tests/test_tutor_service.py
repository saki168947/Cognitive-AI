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


def test_tutor_answers_single_known_concept_token(app):
    with app.app_context():
        seed_courses()

        result = TutorService.answer("What is attention?", course_id="brain-cog-intro")

    assert result["insufficient_evidence"] is False
    assert result["citations"]
    assert "attention" in result["answer"].lower()


def test_tutor_concept_scope_does_not_cite_unrelated_chapters(app):
    with app.app_context():
        seed_courses()

        result = TutorService.answer(
            "reward learning",
            course_id="brain-cog-intro",
            concept_id="concept-human-attention",
        )

    assert result["insufficient_evidence"] is True
    assert result["citations"] == []


def test_tutor_api_rejects_non_string_context_fields(client):
    res = client.post(
        "/api/tutor/ask",
        json={
            "question": "What is attention?",
            "course_id": ["ai-intro"],
        },
    )
    payload = res.get_json()

    assert res.status_code == 400
    assert payload == {"success": False, "error": "course_id must be a string"}
