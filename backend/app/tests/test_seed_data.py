from app.services.seed_data import seed_courses
from app.services.course_service import CourseService


def test_seed_courses_create_two_courses(app):
    seed_courses()

    courses = CourseService.list_courses()

    assert len(courses) == 2
    titles = {course.title for course in courses}
    assert "人工智能导论" in titles
    assert "脑与认知科学导论" in titles


def test_seed_courses_include_cross_course_concepts(app):
    seed_courses()

    graph = CourseService.get_graph()
    labels = {node["label"] for node in graph["nodes"]}
    relationships = {edge["relationship"] for edge in graph["edges"]}

    assert "Transformer Attention" in labels
    assert "Human Attention" in labels
    assert "RELATED_TO" in relationships
