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
        try:
            return json.loads(item.payload_json or "{}")
        except json.JSONDecodeError as exc:
            raise ValueError("Review payload must be valid JSON.") from exc

    @staticmethod
    def _ensure_draft(item, action):
        if item.status != "draft":
            raise ValueError(f"Only draft items can be {action}.")

    @staticmethod
    def _validate_graph_payload(item):
        payload = ReviewService.get_payload(item)
        if not isinstance(payload, dict):
            raise ValueError("Review payload must be an object.")

        payload_course_id = payload.get("course_id")
        concepts = payload.get("concepts", [])
        edges = payload.get("edges", [])
        if not isinstance(concepts, list):
            raise ValueError("Review payload concepts must be a list.")
        if not isinstance(edges, list):
            raise ValueError("Review payload edges must be a list.")

        normalized_concepts = []
        payload_concept_ids = set()
        for concept in concepts:
            if not isinstance(concept, dict):
                raise ValueError("Each concept must be an object.")
            course_id = concept.get("course_id") or payload_course_id
            concept_id = concept.get("id")
            label = concept.get("label")
            if not course_id:
                raise ValueError("Concept course_id is required.")
            if not concept_id:
                raise ValueError("Concept id is required.")
            if not label:
                raise ValueError("Concept label is required.")
            normalized_concepts.append({
                "id": concept_id,
                "course_id": course_id,
                "label": label,
                "definition": concept.get("definition", ""),
            })
            payload_concept_ids.add(concept_id)

        normalized_edges = []
        for edge in edges:
            if not isinstance(edge, dict):
                raise ValueError("Each edge must be an object.")
            course_id = edge.get("course_id") or payload_course_id
            edge_id = edge.get("id")
            source_id = edge.get("source")
            target_id = edge.get("target")
            relationship = edge.get("relationship")
            if not course_id:
                raise ValueError("Edge course_id is required.")
            if not edge_id:
                raise ValueError("Edge id is required.")
            if not source_id:
                raise ValueError("Edge source is required.")
            if not target_id:
                raise ValueError("Edge target is required.")
            if not relationship:
                raise ValueError("Edge relationship is required.")

            for endpoint_name, concept_id in (("source", source_id), ("target", target_id)):
                if concept_id in payload_concept_ids:
                    continue
                concept = db.session.get(Concept, concept_id)
                if concept is None:
                    raise ValueError(f"Edge {endpoint_name} concept does not exist: {concept_id}")
                if concept.status != "published":
                    raise ValueError(f"Edge {endpoint_name} concept is not published: {concept_id}")

            normalized_edges.append({
                "id": edge_id,
                "course_id": course_id,
                "source_id": source_id,
                "target_id": target_id,
                "relationship": relationship,
                "evidence": edge.get("evidence", ""),
            })

        return normalized_concepts, normalized_edges

    @staticmethod
    def approve_item(item_id, reviewer="", notes=""):
        item = db.get_or_404(ReviewItem, item_id)
        ReviewService._ensure_draft(item, "approved")
        item.status = "reviewed"
        item.reviewer = reviewer
        item.decision_notes = notes
        db.session.commit()
        return item

    @staticmethod
    def reject_item(item_id, reviewer="", notes=""):
        item = db.get_or_404(ReviewItem, item_id)
        ReviewService._ensure_draft(item, "rejected")
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

        concepts, edges = ReviewService._validate_graph_payload(item)
        try:
            for concept in concepts:
                db.session.merge(
                    Concept(
                        id=concept["id"],
                        course_id=concept["course_id"],
                        label=concept["label"],
                        definition=concept["definition"],
                        status="published",
                    )
                )
            for edge in edges:
                db.session.merge(
                    GraphEdge(
                        id=edge["id"],
                        course_id=edge["course_id"],
                        source_id=edge["source_id"],
                        target_id=edge["target_id"],
                        relationship=edge["relationship"],
                        status="published",
                        evidence=edge["evidence"],
                    )
                )
            item.status = "published"
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        return item
