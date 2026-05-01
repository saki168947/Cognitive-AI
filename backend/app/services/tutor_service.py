import re

from app.models import Chapter
from app.services.course_service import CourseService


_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "for",
    "how",
    "in",
    "is",
    "of",
    "or",
    "the",
    "to",
    "what",
}


def _tokens(text):
    return {
        token
        for token in re.findall(r"[a-z0-9]+", (text or "").lower())
        if len(token) > 2 and token not in _STOPWORDS
    }


def _score(query_tokens, text):
    return len(query_tokens & _tokens(text))


def _snippet(*parts):
    text = " ".join(part for part in parts if part).strip()
    return text[:240]


class TutorService:
    @staticmethod
    def answer(question, course_id=None, chapter_id=None, concept_id=None):
        query_tokens = _tokens(question)
        graph = CourseService.get_graph(course_id=course_id)
        concepts_by_id = {node["id"]: node for node in graph["nodes"]}
        citations = []

        for edge in graph["edges"]:
            source = concepts_by_id.get(edge["source"], {})
            target = concepts_by_id.get(edge["target"], {})
            if concept_id and concept_id not in {edge["source"], edge["target"]}:
                continue
            text = " ".join(
                [
                    source.get("label", ""),
                    source.get("definition", ""),
                    target.get("label", ""),
                    target.get("definition", ""),
                    edge.get("relationship", ""),
                    edge.get("evidence", ""),
                ]
            )
            if _score(query_tokens, text) >= 2:
                citations.append(
                    {
                        "type": "graph_edge",
                        "id": edge["id"],
                        "title": f"{source.get('label', edge['source'])} {edge['relationship']} {target.get('label', edge['target'])}",
                        "snippet": _snippet(edge.get("evidence", "")),
                    }
                )

        for concept in graph["nodes"]:
            if concept_id and concept["id"] != concept_id:
                continue
            if _score(query_tokens, f"{concept['label']} {concept['definition']}") >= 2:
                citations.append(
                    {
                        "type": "concept",
                        "id": concept["id"],
                        "title": concept["label"],
                        "snippet": _snippet(concept.get("definition", "")),
                    }
                )

        chapters_query = Chapter.query
        if course_id:
            chapters_query = chapters_query.filter_by(course_id=course_id)
        if chapter_id:
            chapters_query = chapters_query.filter_by(id=chapter_id)
        for chapter in chapters_query.order_by(Chapter.order.asc()).all():
            text = f"{chapter.title} {chapter.objectives} {chapter.body}"
            if _score(query_tokens, text) >= 2:
                citations.append(
                    {
                        "type": "chapter",
                        "id": chapter.id,
                        "title": chapter.title,
                        "snippet": _snippet(chapter.objectives, chapter.body),
                    }
                )

        if not citations:
            return {
                "answer": "I do not have enough published course evidence to answer this question.",
                "citations": [],
                "insufficient_evidence": True,
            }

        evidence = citations[0]
        answer = f"Based on published course evidence, {evidence['title']}: {evidence['snippet']}"
        return {
            "answer": answer,
            "citations": citations[:5],
            "insufficient_evidence": False,
        }
