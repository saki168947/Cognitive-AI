"""Users API: lightweight identity for students and teachers."""

from flask import jsonify, request

from app.api import api_bp
from app.services.user_service import UserService


@api_bp.get("/users")
def list_users():
    role = request.args.get("role")
    users = UserService.list_users(role=role)
    return jsonify({"success": True, "data": [UserService.serialize(u) for u in users]})


@api_bp.post("/users")
def create_user():
    body = request.get_json(silent=True) or {}
    name = body.get("name")
    email = body.get("email", "")
    role = body.get("role", "student")
    try:
        user = UserService.create_user(name=name, email=email, role=role)
    except ValueError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    return jsonify({"success": True, "data": UserService.serialize(user)})


@api_bp.get("/users/<user_id>")
def get_user(user_id):
    user = UserService.get_user(user_id)
    if user is None:
        return jsonify({"success": False, "error": f"user not found: {user_id}"}), 404
    return jsonify({"success": True, "data": UserService.serialize(user)})
