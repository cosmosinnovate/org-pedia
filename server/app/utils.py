from datetime import timedelta, datetime
from flask import jsonify
from flask_jwt_extended import create_access_token

def generate_response(message, user=None, access_token=None, status_code=200):
    """Generate a standardized JSON response"""
    response = {
        "message": message,
        "status": "success" if status_code < 400 else "error",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if user:
        response["user"] = user.to_dict() if hasattr(user, 'to_dict') else user
    if access_token:
        response["access_token"] = access_token
        
    return jsonify(response), status_code
    
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