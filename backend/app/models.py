from datetime import datetime, timezone

from .db import db


def utc_now():
    return datetime.now(timezone.utc)


class Course(db.Model):
    id = db.Column(db.String, primary_key=True)
    title = db.Column(db.String, nullable=False)
    summary = db.Column(db.Text, nullable=False, default="")
    status = db.Column(db.String, nullable=False, default="published")
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)


class Chapter(db.Model):
    id = db.Column(db.String, primary_key=True)
    course_id = db.Column(db.String, db.ForeignKey("course.id"), nullable=False)
    order = db.Column(db.Integer, nullable=False, default=0)
    title = db.Column(db.String, nullable=False)
    objectives = db.Column(db.Text, nullable=False, default="")
    body = db.Column(db.Text, nullable=False, default="")
    course = db.relationship("Course", backref=db.backref("chapters", lazy=True))


class LearningActivity(db.Model):
    id = db.Column(db.String, primary_key=True)
    course_id = db.Column(db.String, db.ForeignKey("course.id"), nullable=False)
    chapter_id = db.Column(db.String, db.ForeignKey("chapter.id"), nullable=True)
    title = db.Column(db.String, nullable=False)
    activity_type = db.Column(db.String, nullable=False, default="reading")
    summary = db.Column(db.Text, nullable=False, default="")
    status = db.Column(db.String, nullable=False, default="draft")
    provider = db.Column(db.String, nullable=False, default="manual")
    launch_url = db.Column(db.Text, nullable=False, default="")
    config_json = db.Column(db.Text, nullable=False, default="{}")
    linked_concept_ids_json = db.Column(db.Text, nullable=False, default="[]")
    estimated_minutes = db.Column(db.Integer, nullable=False, default=20)
    release_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)
    course = db.relationship("Course", backref=db.backref("activities", lazy=True))
    chapter = db.relationship("Chapter", backref=db.backref("activities", lazy=True))


class Concept(db.Model):
    id = db.Column(db.String, primary_key=True)
    course_id = db.Column(db.String, db.ForeignKey("course.id"), nullable=False)
    label = db.Column(db.String, nullable=False)
    definition = db.Column(db.Text, nullable=False, default="")
    status = db.Column(db.String, nullable=False, default="published")


class GraphEdge(db.Model):
    id = db.Column(db.String, primary_key=True)
    course_id = db.Column(db.String, db.ForeignKey("course.id"), nullable=False)
    source_id = db.Column(db.String, db.ForeignKey("concept.id"), nullable=False)
    target_id = db.Column(db.String, db.ForeignKey("concept.id"), nullable=False)
    relationship = db.Column(db.String, nullable=False)
    status = db.Column(db.String, nullable=False, default="published")
    evidence = db.Column(db.Text, nullable=False, default="")
    source = db.relationship("Concept", foreign_keys=[source_id], backref=db.backref("outgoing_edges", lazy=True))
    target = db.relationship("Concept", foreign_keys=[target_id], backref=db.backref("incoming_edges", lazy=True))


class QuizItem(db.Model):
    id = db.Column(db.String, primary_key=True)
    chapter_id = db.Column(db.String, db.ForeignKey("chapter.id"), nullable=False)
    prompt = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    explanation = db.Column(db.Text, nullable=False, default="")


class ReviewItem(db.Model):
    id = db.Column(db.String, primary_key=True)
    title = db.Column(db.String, nullable=False)
    item_type = db.Column(db.String, nullable=False, default="graph_suggestion")
    status = db.Column(db.String, nullable=False, default="draft")
    payload_json = db.Column(db.Text, nullable=False, default="{}")
    reviewer = db.Column(db.String, nullable=False, default="")
    decision_notes = db.Column(db.Text, nullable=False, default="")
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)


class Material(db.Model):
    id = db.Column(db.String, primary_key=True)
    course_id = db.Column(db.String, db.ForeignKey("course.id"), nullable=False)
    filename = db.Column(db.String, nullable=False)
    path = db.Column(db.String, nullable=False)
    parser_status = db.Column(db.String, nullable=False, default="uploaded")
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)
    course = db.relationship("Course", backref=db.backref("materials", lazy=True))


class Chunk(db.Model):
    id = db.Column(db.String, primary_key=True)
    material_id = db.Column(db.String, db.ForeignKey("material.id"), nullable=False)
    text = db.Column(db.Text, nullable=False)
    citation_locator = db.Column(db.String, nullable=False, default="")
    material = db.relationship("Material", backref=db.backref("chunks", lazy=True))
