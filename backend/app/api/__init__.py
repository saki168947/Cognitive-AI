from flask import Blueprint

api_bp = Blueprint("api", __name__, url_prefix="/api")

from . import courses  # noqa: E402,F401
from . import graph  # noqa: E402,F401
