from flask import jsonify, request

from app.api import api_bp
from app.models import Material
from app.services.material_service import MaterialService


def _serialize(material):
    return {
        "id": material.id,
        "course_id": material.course_id,
        "filename": material.filename,
        "parser_status": material.parser_status,
    }


@api_bp.post("/materials/upload")
def upload_material():
    course_id = request.form.get("course_id")
    file_storage = request.files.get("file")
    if not course_id or file_storage is None:
        return jsonify({"success": False, "error": "course_id and file are required"}), 400

    material = MaterialService.save_upload(course_id, file_storage)
    review_item = MaterialService.create_review_suggestion_from_material(material)
    return jsonify({
        "success": True,
        "data": {
            "material": _serialize(material),
            "review_item_id": review_item.id,
        },
    })


@api_bp.get("/materials")
def list_materials():
    query = Material.query
    course_id = request.args.get("course_id")
    if course_id:
        query = query.filter_by(course_id=course_id)
    materials = query.order_by(Material.created_at.desc()).all()
    return jsonify({"success": True, "data": [_serialize(material) for material in materials]})
