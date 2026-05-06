"""Assignment & Submission service: teacher assigns work, students submit."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from uuid import uuid4

from app.db import db
from app.models import Assignment, Course, Chapter, LearningActivity, Submission, User, utc_now


_ALLOWED_TYPES = {"reading", "quiz", "code_lab", "experiment", "reflection", "upload"}
_ALLOWED_STATUSES = {"draft", "published", "archived"}


def _parse_datetime(value):
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError as exc:
            raise ValueError(f"invalid datetime: {value}") from exc
    raise ValueError(f"unsupported datetime value: {value!r}")


class AssignmentService:
    @staticmethod
    def create_assignment(
        course_id: str,
        title: str,
        assignment_type: str = "reading",
        description: str = "",
        chapter_id: str | None = None,
        activity_id: str | None = None,
        config: dict | None = None,
        created_by: str | None = None,
        due_at=None,
        status: str = "draft",
        commit: bool = True,
    ) -> Assignment:
        if not course_id or not isinstance(course_id, str):
            raise ValueError("course_id is required")
        if db.session.get(Course, course_id) is None:
            raise ValueError(f"course not found: {course_id}")
        if not title or not isinstance(title, str):
            raise ValueError("title is required")
        if assignment_type not in _ALLOWED_TYPES:
            raise ValueError(f"assignment_type must be one of {_ALLOWED_TYPES}")
        if status not in _ALLOWED_STATUSES:
            raise ValueError(f"status must be one of {_ALLOWED_STATUSES}")
        if chapter_id is not None:
            chapter = db.session.get(Chapter, chapter_id)
            if chapter is None or chapter.course_id != course_id:
                raise ValueError(f"chapter does not belong to course: {chapter_id}")
        if activity_id is not None:
            activity = db.session.get(LearningActivity, activity_id)
            if activity is None or activity.course_id != course_id:
                raise ValueError(f"activity does not belong to course: {activity_id}")
        if created_by is not None and db.session.get(User, created_by) is None:
            raise ValueError(f"creator user not found: {created_by}")

        assignment = Assignment(
            id=f"assignment-{uuid4().hex}",
            course_id=course_id,
            chapter_id=chapter_id,
            activity_id=activity_id,
            title=title,
            description=description or "",
            assignment_type=assignment_type,
            config_json=json.dumps(config or {}, ensure_ascii=False),
            created_by=created_by,
            due_at=_parse_datetime(due_at),
            status=status,
        )
        db.session.add(assignment)
        if commit:
            db.session.commit()
        else:
            db.session.flush()
        db.session.refresh(assignment)
        return assignment

    @staticmethod
    def publish(assignment_id: str) -> Assignment:
        assignment = db.get_or_404(Assignment, assignment_id)
        if assignment.status == "archived":
            raise ValueError("archived assignments cannot be published")
        assignment.status = "published"
        db.session.commit()
        return assignment

    @staticmethod
    def archive(assignment_id: str) -> Assignment:
        assignment = db.get_or_404(Assignment, assignment_id)
        assignment.status = "archived"
        db.session.commit()
        return assignment

    @staticmethod
    def list_assignments(course_id: str | None = None, status: str | None = None) -> list[Assignment]:
        query = Assignment.query
        if course_id:
            query = query.filter_by(course_id=course_id)
        if status:
            query = query.filter_by(status=status)
        return query.order_by(Assignment.created_at.desc()).all()

    @staticmethod
    def get_assignment(assignment_id: str) -> Assignment | None:
        return db.session.get(Assignment, assignment_id)

    @staticmethod
    def serialize(assignment: Assignment) -> dict:
        try:
            config = json.loads(assignment.config_json or "{}")
        except json.JSONDecodeError:
            config = {}
        return {
            "id": assignment.id,
            "course_id": assignment.course_id,
            "chapter_id": assignment.chapter_id,
            "activity_id": assignment.activity_id,
            "title": assignment.title,
            "description": assignment.description,
            "assignment_type": assignment.assignment_type,
            "config": config,
            "created_by": assignment.created_by,
            "due_at": assignment.due_at.isoformat() if assignment.due_at else None,
            "status": assignment.status,
            "created_at": assignment.created_at.isoformat() if assignment.created_at else None,
            "submission_count": len(assignment.submissions or []),
        }


class SubmissionService:
    @staticmethod
    def submit(
        assignment_id: str,
        student_id: str,
        content: dict | None = None,
        commit: bool = True,
    ) -> Submission:
        assignment = db.session.get(Assignment, assignment_id)
        if assignment is None:
            raise ValueError(f"assignment not found: {assignment_id}")
        if assignment.status != "published":
            raise ValueError("can only submit to published assignments")
        student = db.session.get(User, student_id)
        if student is None:
            raise ValueError(f"student not found: {student_id}")
        if student.role != "student":
            raise ValueError("only students can submit")

        submission = Submission(
            id=f"submission-{uuid4().hex}",
            assignment_id=assignment_id,
            student_id=student_id,
            content_json=json.dumps(content or {}, ensure_ascii=False),
            status="submitted",
        )
        db.session.add(submission)
        if commit:
            db.session.commit()
        else:
            db.session.flush()
        db.session.refresh(submission)
        return submission

    @staticmethod
    def grade(
        submission_id: str,
        score: float | None = None,
        feedback: str = "",
        commit: bool = True,
    ) -> Submission:
        submission = db.get_or_404(Submission, submission_id)
        if score is not None:
            try:
                submission.score = float(score)
            except (TypeError, ValueError) as exc:
                raise ValueError(f"score must be numeric: {score!r}") from exc
        submission.feedback = feedback or ""
        submission.status = "graded"
        submission.graded_at = utc_now()
        if commit:
            db.session.commit()
        return submission

    @staticmethod
    def list_for_assignment(assignment_id: str) -> list[Submission]:
        return Submission.query.filter_by(assignment_id=assignment_id).order_by(Submission.submitted_at.desc()).all()

    @staticmethod
    def list_for_student(student_id: str) -> list[Submission]:
        return Submission.query.filter_by(student_id=student_id).order_by(Submission.submitted_at.desc()).all()

    @staticmethod
    def serialize(submission: Submission) -> dict:
        try:
            content = json.loads(submission.content_json or "{}")
        except json.JSONDecodeError:
            content = {}
        return {
            "id": submission.id,
            "assignment_id": submission.assignment_id,
            "student_id": submission.student_id,
            "content": content,
            "status": submission.status,
            "score": submission.score,
            "feedback": submission.feedback,
            "submitted_at": submission.submitted_at.isoformat() if submission.submitted_at else None,
            "graded_at": submission.graded_at.isoformat() if submission.graded_at else None,
        }
