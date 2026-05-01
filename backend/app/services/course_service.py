from app.db import db
from app.models import Chapter, Concept, Course, GraphEdge, QuizItem


class CourseService:
    @staticmethod
    def list_courses():
        return Course.query.order_by(Course.title.asc()).all()

    @staticmethod
    def get_course(course_id):
        return Course.query.get(course_id)

    @staticmethod
    def get_course_detail(course_id):
        course = Course.query.get_or_404(course_id)
        chapters = Chapter.query.filter_by(course_id=course_id).order_by(Chapter.order.asc()).all()
        return {
            "id": course.id,
            "title": course.title,
            "summary": course.summary,
            "chapters": [
                {
                    "id": chapter.id,
                    "title": chapter.title,
                    "order": chapter.order,
                    "objectives": chapter.objectives,
                    "body": chapter.body,
                }
                for chapter in chapters
            ],
        }

    @staticmethod
    def get_chapter(chapter_id):
        chapter = Chapter.query.get_or_404(chapter_id)
        quiz_items = QuizItem.query.filter_by(chapter_id=chapter_id).all()
        return {
            "id": chapter.id,
            "course_id": chapter.course_id,
            "title": chapter.title,
            "objectives": chapter.objectives,
            "body": chapter.body,
            "quiz_items": [
                {
                    "id": item.id,
                    "prompt": item.prompt,
                    "answer": item.answer,
                    "explanation": item.explanation,
                }
                for item in quiz_items
            ],
        }

    @staticmethod
    def get_graph(course_id=None):
        concepts = Concept.query.filter_by(status="published").all()
        edges = GraphEdge.query.filter_by(status="published").all()
        nodes = [
            {
                "id": concept.id,
                "label": concept.label,
                "type": "Concept",
                "definition": concept.definition,
            }
            for concept in concepts
        ]
        return {
            "nodes": nodes,
            "edges": [
                {
                    "id": edge.id,
                    "source": edge.source_id,
                    "target": edge.target_id,
                    "relationship": edge.relationship,
                    "evidence": edge.evidence,
                }
                for edge in edges
            ],
        }

    @staticmethod
    def reset_all():
        for model in (QuizItem, GraphEdge, Concept, Chapter, Course):
            db.session.query(model).delete()
        db.session.commit()
