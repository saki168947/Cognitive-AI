from app.models import Concept, Course, GraphEdge
from app.services.course_service import CourseService
from app.services.seed_data import seed_courses


def test_seed_courses_create_two_courses(app):
    seed_courses()

    courses = CourseService.list_courses()

    assert len(courses) == 2
    titles = {course.title for course in courses}
    assert "人工智能导论" in titles
    assert "脑与认知科学导论" in titles


def test_seed_courses_are_idempotent(app):
    seed_courses()
    seed_courses()

    graph = CourseService.get_graph()

    assert Course.query.count() == 2
    assert len(graph["nodes"]) == 5
    assert len({node["id"] for node in graph["nodes"]}) == 5
    assert len(graph["edges"]) == 3
    assert len({edge["id"] for edge in graph["edges"]}) == 3
    assert Concept.query.count() == len(graph["nodes"])
    assert GraphEdge.query.count() == len(graph["edges"])


def test_seed_courses_include_cross_course_concepts(app):
    seed_courses()

    graph = CourseService.get_graph()
    labels = {node["label"] for node in graph["nodes"]}
    relationships = {edge["relationship"] for edge in graph["edges"]}

    assert "Transformer Attention" in labels
    assert "Human Attention" in labels
    assert "RELATED_TO" in relationships


def test_ai_intro_graph_includes_connected_cross_course_concepts(app):
    seed_courses()

    graph = CourseService.get_graph("ai-intro")
    labels = {node["label"] for node in graph["nodes"]}

    assert "Transformer Attention" in labels
    assert "Human Attention" in labels
    assert "Reward System" in labels


def test_brain_cog_intro_graph_includes_human_attention(app):
    seed_courses()

    graph = CourseService.get_graph("brain-cog-intro")
    labels = {node["label"] for node in graph["nodes"]}

    assert "Human Attention" in labels
    assert "Heuristic Search" not in labels
    assert "Transformer Attention" not in labels
