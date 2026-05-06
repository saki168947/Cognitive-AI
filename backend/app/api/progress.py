"""Progress API: record events and read summaries."""

from flask import jsonify, request

from app.api import api_bp
from app.services.progress_service import ProgressService


@api_bp.post("/progress/events")
def record_event():
    body = request.get_json(silent=True) or {}
    try:
        event = ProgressService.record(
            student_id=body.get("student_id"),
            event_type=body.get("event_type"),
            course_id=body.get("course_id"),
            chapter_id=body.get("chapter_id"),
            activity_id=body.get("activity_id"),
            payload=body.get("payload") or {},
        )
    except ValueError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    return jsonify({"success": True, "data": {"id": event.id}})


@api_bp.get("/progress/students/<student_id>")
def student_summary(student_id):
    return jsonify({"success": True, "data": ProgressService.summary_for_student(student_id)})


@api_bp.get("/progress/courses/<course_id>")
def cohort_summary(course_id):
    return jsonify({"success": True, "data": ProgressService.cohort_summary(course_id)})
