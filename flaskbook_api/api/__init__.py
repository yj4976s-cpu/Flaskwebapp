from flask import Blueprint, jsonify, request
from flaskbook_api.api import calculation

api = Blueprint("api", __name__)

@api.get("/")
def index():
    return jsonify({"column": "value"}), 201

@api.post("/detect")
def detection():
    return calculation.detection(request)

# def create_app(config_name):
#     app = Flask(__name__)
#     app.config.from_object(config[config_name])
#     return app