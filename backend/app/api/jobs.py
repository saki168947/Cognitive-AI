"""Job status API."""

from flask import jsonify

from app.api import api_bp
from app.services.job_queue import get_queue


@api_bp.get("/jobs/<job_id>")
def get_job(job_id):
    queue = get_queue()
    job = queue.get(job_id)
    if job is None:
        return jsonify({"success": False, "error": f"job not found: {job_id}"}), 404
    return jsonify({"success": True, "data": queue.serialize(job)})
