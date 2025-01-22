

def generate_response(message, user, access_token, status_code):
    return jsonify({
        "message": message,
        "access_token": access_token,
        "user": user.to_dict(),
    }), status_code
    
    
    
# Helper functions
def generate_jwt(user: User) -> str:
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