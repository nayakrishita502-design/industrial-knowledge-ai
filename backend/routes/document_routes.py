import os

from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename
from config import Config
from utils.files_utils import allowed_file, get_file_size

document_bp = Blueprint("document_bp", __name__)


@document_bp.route("/upload", methods=["POST"])
def upload_document():

    if "file" not in request.files:
        return jsonify({
            "success": False,
            "message": "No file selected."
        }), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({
            "success": False,
            "message": "Filename is empty."
        }), 400

    if not allowed_file(file.filename):
        return jsonify({
            "success": False,
            "message": "Unsupported file type."
        }), 400

    filename = secure_filename(file.filename)

    save_path = os.path.join(
        Config.UPLOAD_FOLDER,
        filename
    )

    file.save(save_path)

    return jsonify({
        "success": True,
        "filename": filename,
        "size": get_file_size(save_path),
        "message": "File uploaded successfully."
    })