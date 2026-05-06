"""Background job handlers.

Each handler implements the heavy work for a specific job type.
Handlers receive the Flask app instance so they can push their own app_context.
"""

from __future__ import annotations

import logging

from app.db import db
from app.models import Material
from app.services.job_queue import JobContext, register_handler

logger = logging.getLogger(__name__)


@register_handler("ingest_material")
def handle_ingest_material(app, job_id: str, payload: dict, ctx: JobContext) -> dict:
    """Heavy material processing: extract → chunk → embed → LLM concept extraction.

    Assumes the file is already saved and the Material row exists.
    """
    from app.services.material_service import MaterialService

    material_id = payload.get("material_id")
    if not material_id:
        raise ValueError("payload.material_id is required")

    with app.app_context():
        material = db.session.get(Material, material_id)
        if material is None:
            raise ValueError(f"material not found: {material_id}")

        ctx.update(progress=10, message="Extracting and chunking text")
        chunks = MaterialService.extract_and_chunk(material, commit=True)
        if not chunks:
            return {"chunks": 0, "review_item_id": None, "note": "no extractable text"}

        ctx.update(progress=40, message=f"Embedding {len(chunks)} chunks")
        try:
            MaterialService.embed_and_store(material, chunks)
            db.session.commit()
        except Exception:
            logger.exception("Embedding failed; continuing without vector index")
            material.parser_status = "chunked"
            db.session.commit()

        ctx.update(progress=70, message="Extracting concepts via LLM")
        review_item = MaterialService.create_review_suggestion_from_chunks(
            material, chunks, commit=True
        )

        ctx.update(progress=100, message="Done")
        return {
            "material_id": material_id,
            "chunks": len(chunks),
            "review_item_id": review_item.id if review_item else None,
            "parser_status": material.parser_status,
        }
