import os
import re
from uuid import uuid4

from flask import current_app
from werkzeug.utils import secure_filename

from app.db import db
from app.models import Chunk, Material
from app.services.review_service import ReviewService


class MaterialService:
    @staticmethod
    def save_upload(course_id, file_storage):
        upload_dir = current_app.config["UPLOAD_DIR"]
        os.makedirs(upload_dir, exist_ok=True)
        filename = secure_filename(file_storage.filename or "upload")
        path = os.path.join(upload_dir, filename)
        file_storage.save(path)

        material = Material(
            id=f"material-{uuid4().hex}",
            course_id=course_id,
            filename=filename,
            path=path,
        )
        db.session.add(material)
        db.session.commit()
        db.session.refresh(material)
        return material

    @staticmethod
    def extract_text(material):
        with open(material.path, "rb") as handle:
            return handle.read().decode("utf-8", errors="ignore")

    @staticmethod
    def chunk_material(material):
        text = MaterialService.extract_text(material)
        parts = [part.strip()[:1200] for part in re.split(r"\n\s*\n", text) if part.strip()]
        if not parts and text.strip():
            parts = [text.strip()[:1200]]
        parts = parts[:20]

        chunks = []
        for index, part in enumerate(parts, start=1):
            chunk = Chunk(
                id=f"chunk-{material.id}-{index}",
                material_id=material.id,
                text=part,
                citation_locator=f"{material.filename}#chunk-{index}",
            )
            db.session.add(chunk)
            chunks.append(chunk)

        material.parser_status = "chunked"
        db.session.commit()
        return chunks

    @staticmethod
    def create_review_suggestion_from_material(material):
        chunks = MaterialService.chunk_material(material)
        payload = {
            "course_id": material.course_id,
            "concepts": [{
                "id": f"concept-upload-{material.id}",
                "course_id": material.course_id,
                "label": material.filename.rsplit(".", 1)[0],
                "definition": chunks[0].text[:240] if chunks else "Uploaded course material.",
            }],
            "edges": [],
        }
        return ReviewService.create_graph_suggestion(
            title=f"Uploaded material: {material.filename}",
            payload=payload,
        )
