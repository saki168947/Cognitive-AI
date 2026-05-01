from app.services.seed_data import seed_courses


def test_list_courses_returns_seed_courses(client, app):
    with app.app_context():
        seed_courses()

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
