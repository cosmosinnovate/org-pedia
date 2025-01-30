from xml.dom import ValidationErr
from flask import Blueprint, jsonify, request
from app.schemas.schemas import UserSchema
from app.utils import generate_response, generate_jwt
from app.services.user_service import UserService as user_service

auth_bp = Blueprint('auth', __name__)
user_schema = UserSchema()

@auth_bp.route("/register", methods=["POST"])
def authentication():
    data = request.get_json()
    user, access_token = user_service.create_user(data)
    return generate_response("Signed in successfully", user, access_token, 200 if user else 201)