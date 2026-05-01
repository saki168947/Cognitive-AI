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
