from datetime import datetime, timedelta, timezone
import os
from uuid import uuid4
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
from pydantic import BaseModel
from flask_migrate import Migrate
import ollama
import json

from sqlalchemy import JSON, DateTime

# Flask app initialization
app = Flask(__name__)
CORS(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:postgres@localhost/org_pedia"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")

# Extensions initialization
db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

# Models
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    display_name = db.Column(db.String, index=True)
    email = db.Column(db.String, unique=True, index=True)
    photo_url = db.Column(db.String)
    access_token = db.Column(db.String)

    def __init__(self, display_name=None, email=None, photo_url=None, access_token=None):
        self.display_name = display_name
        self.email = email
        self.photo_url = photo_url
        self.access_token = access_token

    def to_dict(self):
        return {
            "id": self.id,
            "display_name": self.display_name,
            "email": self.email,
            "photo_url": self.photo_url,
            "access_token": self.access_token,
        }

class Message(db.Model):
    __tablename__ = "chat_history"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    messages = db.Column(JSON)
    created_at = db.Column(DateTime, index=True, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f"Message(id={self.id}, id={self.id}, messages='{str(self.messages)[:20]}...')"

# Pydantic models
class ChatCreate(BaseModel):
    messages: list = []

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

# Routes
@app.route("/auth", methods=["POST"])
def authenticate_google():
    data = request.get_json()
    user = User.query.filter_by(email=data.get("email")).first()
    
    if user:
        User.update_user(user, data)
        access_token = generate_jwt(user)
        return jsonify({
            "message": "Signed in successfully",
            "access_token": access_token,
            "user": user.to_dict()
        }), 200

    required_fields = ["id", "display_name", "email", "photo_url", "access_token"]
    if not all(field in data for field in required_fields):
        return jsonify({"message": "All required fields must be provided"}), 400

    try:
        new_user = User(
            id=data["id"],
            display_name=data["display_name"],
            email=data["email"],
            photo_url=data["photo_url"],
            access_token=data["access_token"],
        )
        db.session.add(new_user)
        db.session.commit()

        return jsonify({
            "message": "User created successfully",
            "access_token": generate_jwt(new_user),
        }), 201

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify({"message": "Failed to create user"}), 500

@app.route("/chat", methods=["POST"])
def create_chat():
    data = request.json
    id = data.get("id")
    messages = data.get("messages", [])

    new_message = Message(id=id, messages=messages)
    db.session.add(new_message)
    db.session.commit()
    
    return jsonify({"message": "Chat created successfully", "chat_id": new_message.id}), 201

@app.route("/chat/<chat_id>", methods=["PUT"])
def update_chat(chat_id):
    try:
        message = Message.query.get(chat_id)
        if not message:
            return jsonify({"error": "Chat not found"}), 404

        messages = request.json.get("messages", [])
        
        if not isinstance(messages, list):
            messages = [messages]

        def generate():
            response = ollama.chat(
                model="llama3.2",
                messages=messages,
                options={"temperature": 0.9, "max_token": 2000},
                stream=True,
            )

            for part in response:
                content = part.get("message", {}).get("content", "")
                yield f"data: {json.dumps({'content': content})}\n\n"

                if part.get("done"):
                    messages.append({"role": "assistant", "content": content})
                    message.messages = messages
                    db.session.commit()
                    break

            yield "data: [DONE]\n\n"

        return Response(
            generate(),
            headers={
                "Content-Type": "text/event-stream",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            },
        )

    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": "Error processing request"}), 500

@app.route("/", methods=["GET"])
def health():
    return jsonify({"message": "OK"})

if __name__ == "__main__":
    app.run(port=8000)