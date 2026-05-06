"""Assignment & Submission API."""

from flask import jsonify, request

from app.api import api_bp
from app.services.assignment_service import AssignmentService, SubmissionService


@api_bp.get("/assignments")
def list_assignments():
    course_id = request.args.get("course_id")
    status = request.args.get("status")
    items = AssignmentService.list_assignments(course_id=course_id, status=status)
    return jsonify({"success": True, "data": [AssignmentService.serialize(a) for a in items]})


@api_bp.post("/assignments")
def create_assignment():
    body = request.get_json(silent=True) or {}
    try:
        assignment = AssignmentService.create_assignment(
            course_id=body.get("course_id"),
            title=body.get("title"),
            assignment_type=body.get("assignment_type", "reading"),
            description=body.get("description", ""),
            chapter_id=body.get("chapter_id"),
            activity_id=body.get("activity_id"),
            config=body.get("config") or {},
            created_by=body.get("created_by"),
            due_at=body.get("due_at"),
            status=body.get("status", "draft"),
        )
    except ValueError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    return jsonify({"success": True, "data": AssignmentService.serialize(assignment)})


@api_bp.get("/assignments/<assignment_id>")
def get_assignment(assignment_id):
    assignment = AssignmentService.get_assignment(assignment_id)
    if assignment is None:
        return jsonify({"success": False, "error": f"assignment not found: {assignment_id}"}), 404
    return jsonify({"success": True, "data": AssignmentService.serialize(assignment)})


@api_bp.post("/assignments/<assignment_id>/publish")
def publish_assignment(assignment_id):
    try:
        assignment = AssignmentService.publish(assignment_id)
    except ValueError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    return jsonify({"success": True, "data": AssignmentService.serialize(assignment)})


@api_bp.post("/assignments/<assignment_id>/archive")
def archive_assignment(assignment_id):
    try:
        assignment = AssignmentService.archive(assignment_id)
    except ValueError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    return jsonify({"success": True, "data": AssignmentService.serialize(assignment)})


@api_bp.get("/assignments/<assignment_id>/submissions")
def list_submissions(assignment_id):
    submissions = SubmissionService.list_for_assignment(assignment_id)
    return jsonify({"success": True, "data": [SubmissionService.serialize(s) for s in submissions]})


@api_bp.post("/assignments/<assignment_id>/submissions")
def submit_assignment(assignment_id):
    body = request.get_json(silent=True) or {}
    student_id = body.get("student_id")
    content = body.get("content") or {}
    try:
        submission = SubmissionService.submit(assignment_id, student_id, content)
    except ValueError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    return jsonify({"success": True, "data": SubmissionService.serialize(submission)})


@api_bp.post("/submissions/<submission_id>/grade")
def grade_submission(submission_id):
    body = request.get_json(silent=True) or {}
    score = body.get("score")
    feedback = body.get("feedback", "")
    try:
        submission = SubmissionService.grade(submission_id, score=score, feedback=feedback)
    except ValueError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    return jsonify({"success": True, "data": SubmissionService.serialize(submission)})


@api_bp.get("/students/<student_id>/submissions")
def list_student_submissions(student_id):
    submissions = SubmissionService.list_for_student(student_id)
    return jsonify({"success": True, "data": [SubmissionService.serialize(s) for s in submissions]})
