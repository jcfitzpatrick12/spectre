from flask import Blueprint, request, jsonify
from spectre_server.services.capture import start_capture

capture_blueprint = Blueprint("capture", __name__)

@capture_blueprint.route("/start", methods=["POST"])
def start():
    data = request.get_json()
    tag = data.get("tag")
    
    if not tag:
        return jsonify({"error": "Tag is required"}), 400

    # Call the service layer
    result = start_capture(tag)
    return jsonify({"message": result})
