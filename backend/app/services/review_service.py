import json
from uuid import uuid4

from app.db import db
from app.models import Concept, GraphEdge, ReviewItem


class ReviewService:
    @staticmethod
    def list_items():
        return ReviewItem.query.order_by(ReviewItem.created_at.desc()).all()

    @staticmethod
    def create_graph_suggestion(title, payload):
        item = ReviewItem(
            id=f"review-{uuid4().hex}",
            title=title,
            item_type="graph_suggestion",
            status="draft",
            payload_json=json.dumps(payload, ensure_ascii=False),
        )
        db.session.add(item)
        db.session.commit()
        db.session.refresh(item)
        return item

    @staticmethod
    def get_payload(item):
        return json.loads(item.payload_json or "{}")

    @staticmethod
    def approve_item(item_id, reviewer="", notes=""):
        item = db.get_or_404(ReviewItem, item_id)
        item.status = "reviewed"
        item.reviewer = reviewer
        item.decision_notes = notes
        db.session.commit()
        return item

    @staticmethod
    def reject_item(item_id, reviewer="", notes=""):
        item = db.get_or_404(ReviewItem, item_id)
        item.status = "rejected"
        item.reviewer = reviewer
        item.decision_notes = notes
        db.session.commit()
        return item

    @staticmethod
    def publish_item(item_id):
        item = db.get_or_404(ReviewItem, item_id)
        if item.status != "reviewed":
            raise ValueError("Only reviewed items can be published.")

        payload = ReviewService.get_payload(item)
        payload_course_id = payload.get("course_id")
        concepts = payload.get("concepts", [])
        edges = payload.get("edges", [])

        for concept in concepts:
            course_id = concept.get("course_id") or payload_course_id
            if not course_id:
                raise ValueError("Concept course_id is required.")
            if not concept.get("id"):
                raise ValueError("Concept id is required.")
            if not concept.get("label"):
                raise ValueError("Concept label is required.")
            db.session.merge(
                Concept(
                    id=concept["id"],
                    course_id=course_id,
                    label=concept["label"],
                    definition=concept.get("definition", ""),
                    status="published",
                )
            )

        db.session.flush()

        for edge in edges:
            course_id = edge.get("course_id") or payload_course_id
            source_id = edge.get("source")
            target_id = edge.get("target")
            relationship = edge.get("relationship")
            if not course_id:
                raise ValueError("Edge course_id is required.")
            if not edge.get("id"):
                raise ValueError("Edge id is required.")
            if not source_id:
                raise ValueError("Edge source is required.")
            if not target_id:
                raise ValueError("Edge target is required.")
            if not relationship:
                raise ValueError("Edge relationship is required.")
            if db.session.get(Concept, source_id) is None:
                raise ValueError(f"Edge source concept does not exist: {source_id}")
            if db.session.get(Concept, target_id) is None:
                raise ValueError(f"Edge target concept does not exist: {target_id}")
            db.session.merge(
                GraphEdge(
                    id=edge["id"],
                    course_id=course_id,
                    source_id=source_id,
                    target_id=target_id,
                    relationship=relationship,
                    status="published",
                    evidence=edge.get("evidence", ""),
                )
            )

        item.status = "published"
        db.session.commit()
        return item
