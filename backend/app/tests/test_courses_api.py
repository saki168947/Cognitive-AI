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
