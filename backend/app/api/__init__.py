from flask import Blueprint, jsonify
from werkzeug.exceptions import NotFound

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.errorhandler(NotFound)
def handle_not_found(error):
    return jsonify({"success": False, "error": error.description}), 404


from . import courses  # noqa: E402,F401
from . import graph  # noqa: E402,F401
