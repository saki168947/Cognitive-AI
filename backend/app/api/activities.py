from flask import jsonify, request

from app.api import api_bp
from app.services.activity_service import ActivityService
from app.services.seed_data import seed_courses


def _ensure_seeded():
    if not ActivityService.list_activities():
        seed_courses()


@api_bp.get("/activities")
def list_activities():
    _ensure_seeded()
    course_id = request.args.get("course_id")
    status = request.args.get("status")
    activities = ActivityService.list_activities(course_id=course_id, status=status)
    return jsonify({
        "success": True,
        "data": [ActivityService.serialize(activity) for activity in activities],
    })


@api_bp.get("/courses/<course_id>/activities")
def list_course_activities(course_id):
    _ensure_seeded()
    activities = ActivityService.list_for_course(course_id)
    return jsonify({
        "success": True,
        "data": [ActivityService.serialize(activity) for activity in activities],
    })


@api_bp.post("/activities")
def create_activity():
    payload = request.get_json(silent=True)
    if payload is None:
        payload = {}
    if not isinstance(payload, dict):
        return jsonify({"success": False, "error": "request body must be an object."}), 400

    try:
        activity = ActivityService.create_activity(payload)
    except ValueError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400

    return jsonify({"success": True, "data": ActivityService.serialize(activity)}), 201
