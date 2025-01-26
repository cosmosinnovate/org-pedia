from datetime import timedelta
from flask import jsonify
from flask_jwt_extended import create_access_token

def generate_response(message, user, access_token, status_code):
    return jsonify({
        "message": message,
        "access_token": access_token,
        "user": user,
    }), status_code
    
def generate_jwt(user) -> str:
    return create_access_token(
        identity=user.id,
        additional_claims={
            "display_name": user.display_name,
            "email": user.email,
            "photo_url": user.photo_url,
            "id": user.id,
            "access_token": user.access_token,
        },
        expires_delta=timedelta(hours=45),
    )