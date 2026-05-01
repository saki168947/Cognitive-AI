import io
import os

from app.db import db
from app.models import Chunk, Material, ReviewItem
from app.services.review_service import ReviewService
from app.services.seed_data import seed_courses


def test_upload_text_material_creates_chunks_and_review_payload(client, app):
    with app.app_context():
        seed_courses()

    res = client.post(
        "/api/materials/upload",
        data={
            "course_id": "brain-cog-intro",
            "file": (io.BytesIO(b"Attention selects signals.\n\nMemory keeps context."), "lecture.txt"),
        },
        content_type="multipart/form-data",
    )
    payload = res.get_json()

    assert res.status_code == 200
    assert payload["success"] is True
    material_data = payload["data"]["material"]
    assert material_data["course_id"] == "brain-cog-intro"
    assert material_data["filename"] == "lecture.txt"
    assert material_data["parser_status"] == "chunked"
    assert payload["data"]["review_item_id"]

    with app.app_context():
        material = db.session.get(Material, material_data["id"])
        chunks = Chunk.query.filter_by(material_id=material.id).order_by(Chunk.id).all()
        review_item = db.session.get(ReviewItem, payload["data"]["review_item_id"])
        review_payload = ReviewService.get_payload(review_item)

        assert material.parser_status == "chunked"
        assert [chunk.text for chunk in chunks] == ["Attention selects signals.", "Memory keeps context."]
        assert chunks[0].citation_locator == "lecture.txt#chunk-1"
        assert review_payload["course_id"] == "brain-cog-intro"
        assert review_payload["concepts"][0]["course_id"] == "brain-cog-intro"


def test_list_materials_filters_by_course_id(client, app):
    with app.app_context():
        db.session.add_all([
            Material(id="mat-brain", course_id="brain-cog-intro", filename="brain.txt", path="/tmp/brain.txt"),
            Material(id="mat-ai", course_id="ai-intro", filename="ai.txt", path="/tmp/ai.txt"),
        ])
        db.session.commit()

    res = client.get("/api/materials?course_id=brain-cog-intro")
    payload = res.get_json()

    assert res.status_code == 200
    assert payload["success"] is True
    assert [item["id"] for item in payload["data"]] == ["mat-brain"]


def test_upload_requires_course_id_and_file(client):
    missing_course = client.post(
        "/api/materials/upload",
        data={"file": (io.BytesIO(b"text"), "lecture.txt")},
        content_type="multipart/form-data",
    )
    missing_file = client.post(
        "/api/materials/upload",
        data={"course_id": "brain-cog-intro"},
        content_type="multipart/form-data",
    )

    assert missing_course.status_code == 400
    assert missing_course.get_json() == {"success": False, "error": "course_id and file are required"}
    assert missing_file.status_code == 400
    assert missing_file.get_json() == {"success": False, "error": "course_id and file are required"}


def test_upload_uses_app_config_upload_dir(client, app):
    with app.app_context():
        seed_courses()

    res = client.post(
        "/api/materials/upload",
        data={
            "course_id": "brain-cog-intro",
            "file": (io.BytesIO(b"Configured upload path."), "config-path.txt"),
        },
        content_type="multipart/form-data",
    )
    payload = res.get_json()

    assert res.status_code == 200
    with app.app_context():
        material = db.session.get(Material, payload["data"]["material"]["id"])
        assert material.path == os.path.join(app.config["UPLOAD_DIR"], "config-path.txt")
        assert os.path.exists(material.path)
