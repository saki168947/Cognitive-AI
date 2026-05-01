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
    def _secure_upload_filename(file_storage):
        filename = secure_filename(file_storage.filename or "")
        if not filename:
            raise ValueError("file filename is invalid")
        return filename

    @staticmethod
    def save_upload(course_id, file_storage, commit=True):
        upload_dir = current_app.config["UPLOAD_DIR"]
        os.makedirs(upload_dir, exist_ok=True)
        filename = MaterialService._secure_upload_filename(file_storage)
        material_id = f"material-{uuid4().hex}"
        path = os.path.join(upload_dir, f"{material_id}_{filename}")
        file_storage.save(path)

        material = Material(
            id=material_id,
            course_id=course_id,
            filename=filename,
            path=path,
        )
        db.session.add(material)
        if commit:
            db.session.commit()
        else:
            db.session.flush()
        db.session.refresh(material)
        return material

    @staticmethod
    def extract_text(material):
        with open(material.path, "rb") as handle:
            return handle.read().decode("utf-8", errors="ignore")

    @staticmethod
    def chunk_material(material, commit=True):
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
        if commit:
            db.session.commit()
        else:
            db.session.flush()
        return chunks

    @staticmethod
    def create_review_suggestion_from_material(material, commit=True):
        chunks = MaterialService.chunk_material(material, commit=False)
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
            commit=commit,
        )

    @staticmethod
    def ingest_upload(course_id, file_storage):
        saved_path = None
        try:
            material = MaterialService.save_upload(course_id, file_storage, commit=False)
            saved_path = material.path
            review_item = MaterialService.create_review_suggestion_from_material(material, commit=False)
            db.session.commit()
            db.session.refresh(material)
            db.session.refresh(review_item)
            return material, review_item
        except Exception:
            db.session.rollback()
            if saved_path and os.path.exists(saved_path):
                os.remove(saved_path)
            raise
