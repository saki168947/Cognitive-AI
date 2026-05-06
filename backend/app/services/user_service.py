"""User service: lightweight user CRUD without password auth.

Auth is intentionally not handled here — assume an upstream identity provider
(or anonymous student/teacher selection in dev). This service provides the
minimum needed to attribute work to specific people.
"""

from __future__ import annotations

from uuid import uuid4

from app.db import db
from app.models import User


_ALLOWED_ROLES = {"student", "teacher"}


class UserService:
    @staticmethod
    def create_user(name: str, email: str = "", role: str = "student", commit: bool = True) -> User:
        if not name or not isinstance(name, str):
            raise ValueError("name is required")
        if role not in _ALLOWED_ROLES:
            raise ValueError(f"role must be one of {_ALLOWED_ROLES}")
        user = User(
            id=f"user-{uuid4().hex}",
            name=name,
            email=email or "",
            role=role,
        )
        db.session.add(user)
        if commit:
            db.session.commit()
        else:
            db.session.flush()
        db.session.refresh(user)
        return user

    @staticmethod
    def get_user(user_id: str) -> User | None:
        return db.session.get(User, user_id)

    @staticmethod
    def list_users(role: str | None = None) -> list[User]:
        query = User.query
        if role:
            query = query.filter_by(role=role)
        return query.order_by(User.created_at.desc()).all()

    @staticmethod
    def serialize(user: User) -> dict:
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
        }

    @staticmethod
    def get_or_create_default_teacher() -> User:
        """Return a single default teacher user, creating it if missing.

        Useful in dev/MVP where we want assignments to attribute to *someone*
        without forcing real auth.
        """
        default = User.query.filter_by(role="teacher").first()
        if default:
            return default
        return UserService.create_user(name="Default Teacher", role="teacher")
