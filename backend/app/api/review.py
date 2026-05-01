from flask import jsonify, request

from app.api import api_bp
from app.services.review_service import ReviewService


def _serialize(item):
    return {
        "id": item.id,
        "title": item.title,
        "item_type": item.item_type,
        "status": item.status,
        "payload": ReviewService.get_payload(item),
        "reviewer": item.reviewer,
        "decision_notes": item.decision_notes,
    }


@api_bp.get("/review/items")
def list_review_items():
    return jsonify({"success": True, "data": [_serialize(item) for item in ReviewService.list_items()]})


@api_bp.post("/review/items/<item_id>/approve")
def approve_review_item(item_id):
    body = request.get_json(silent=True) or {}
    item = ReviewService.approve_item(
        item_id,
        reviewer=body.get("reviewer", ""),
        notes=body.get("notes", ""),
    )
    return jsonify({"success": True, "data": _serialize(item)})


@api_bp.post("/review/items/<item_id>/reject")
def reject_review_item(item_id):
    body = request.get_json(silent=True) or {}
    item = ReviewService.reject_item(
        item_id,
        reviewer=body.get("reviewer", ""),
        notes=body.get("notes", ""),
    )
    return jsonify({"success": True, "data": _serialize(item)})


@api_bp.post("/review/items/<item_id>/publish")
def publish_review_item(item_id):
    try:
        item = ReviewService.publish_item(item_id)
    except ValueError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    return jsonify({"success": True, "data": _serialize(item)})
