from app.services.seed_data import seed_courses


def test_graph_endpoint_returns_nodes_and_edges(client, app):
    with app.app_context():
        seed_courses()

    res = client.get("/api/graph")
    payload = res.get_json()

    assert res.status_code == 200
    assert payload["success"] is True
    assert any(node["label"] == "Transformer Attention" for node in payload["data"]["nodes"])
    assert any(edge["relationship"] == "RELATED_TO" for edge in payload["data"]["edges"])


def test_graph_endpoint_scopes_nodes_by_course(client, app):
    with app.app_context():
        seed_courses()

    res = client.get("/api/graph?course_id=brain-cog-intro")
    payload = res.get_json()
    labels = {node["label"] for node in payload["data"]["nodes"]}

    assert res.status_code == 200
    assert "Human Attention" in labels
    assert "Heuristic Search" not in labels
