from flask import jsonify, request

from app.api import api_bp
from app.services.course_service import CourseService
from app.services.seed_data import seed_courses
from app.services.tutor_service import TutorService


@api_bp.post("/tutor/ask")
def ask_tutor():
    body = request.get_json(silent=True) or {}
    question = body.get("question", "") if isinstance(body, dict) else ""
    if not isinstance(question, str) or not question.strip():
        return jsonify({"success": False, "error": "question is required"}), 400

    if not CourseService.list_courses():
        seed_courses()

    result = TutorService.answer(
        question,
        course_id=body.get("course_id"),
        chapter_id=body.get("chapter_id"),
        concept_id=body.get("concept_id"),
    )
    return jsonify({"success": True, "data": result})
