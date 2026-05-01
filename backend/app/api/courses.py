from flask import jsonify

from app.api import api_bp
from app.services.course_service import CourseService
from app.services.seed_data import seed_courses


@api_bp.get("/courses")
def list_courses():
    courses = CourseService.list_courses()
    if not courses:
        seed_courses()
        courses = CourseService.list_courses()
    return jsonify({
        "success": True,
        "data": [
            {
                "id": course.id,
                "title": course.title,
                "summary": course.summary,
                "status": course.status,
            }
            for course in courses
        ],
    })


@api_bp.get("/courses/<course_id>")
def get_course(course_id):
    return jsonify({"success": True, "data": CourseService.get_course_detail(course_id)})


@api_bp.get("/chapters/<chapter_id>")
def get_chapter(chapter_id):
    return jsonify({"success": True, "data": CourseService.get_chapter(chapter_id)})
