from datetime import datetime, timedelta, timezone
from operator import index
from optparse import Option
import os
from re import L
from typing import Collection, Optional, List
from uuid import uuid4
from xml.dom import ValidationErr
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
from pydantic import BaseModel
from flask_migrate import Migrate
import ollama
import json
from pydantic import BaseModel
from sqlalchemy import and_
from sqlalchemy.orm import joinedload
from flask import jsonify


from sqlalchemy import JSON, DateTime

# Flask app initialization
app = Flask(__name__)
CORS(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

# Verify that the keys are set
if not app.config['JWT_SECRET_KEY']:
    raise RuntimeError("JWT_SECRET_KEY is not set. Please set it as an environment variable.")
if not app.config['SECRET_KEY']:
    print("Warning: SECRET_KEY is not set. It's recommended to set it for enhanced security.")

# check if database exist
if not app.config['SQLALCHEMY_DATABASE_URI']:
    raise RuntimeError("DATABASE_URL is not set. Please set it as an environment variable.")

# check if database org_pedia is created

# Extensions initialization
db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

# Models
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    display_name = db.Column(db.String, index=True)
    user_google_id = db.Column(db.String)
    email = db.Column(db.String, unique=True, index=True)
    photo_url = db.Column(db.String)
    access_token = db.Column(db.String)

    def __init__(self, user_google_id=None, display_name=None, email=None, photo_url=None, access_token=None):
        self.user_google_id = user_google_id
        self.display_name = display_name
        self.email = email
        self.photo_url = photo_url
        self.access_token = access_token

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "photo_url": self.photo_url,
            "display_name": self.display_name,
            "access_token": self.access_token,
            "user_google_id": self.user_google_id,
        }


# Define a Pydantic model for the incoming user data
class GoogleUserModel(BaseModel):
    user_google_id: str
    display_name: str
    email: str
    photo_url: str
    access_token: str

class Chat(db.Model):
    __tablename__ = "chat_history"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String, index=True, nullable=False)
    messages = db.Column(JSON)
    created_at = db.Column(DateTime, index=True, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f"Message(id={self.id}, id={self.id}, title={self.title} messages='{str(self.messages)[:20]}...')"
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "messages": self.messages,
        }

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
    
# Helper functions
def update_user_repo(user, user_data):
    user.user_google_id = user_data.user_google_id
    user.display_name = user_data.display_name
    user.photo_url = user_data.photo_url
    user.access_token = user_data.access_token
    db.session.commit()
    
def create_user_repo(user_data):
    new_user = User(
        user_google_id=user_data.user_google_id,
        display_name=user_data.display_name,
        email=user_data.email,
        photo_url=user_data.photo_url,
        access_token=user_data.access_token
    )
    db.session.add(new_user)
    db.session.commit()
    return new_user

def update_chat_title(chat_id:str, title:str):
    try:
        chat = db.session.query(Chat).where(Chat.id == chat_id)
        
        return chat.to_dict()
    except Exception as e:
        return None
    
    
def update_chat_repo(chat_id: str, user_id: str, update_data: dict) -> Optional[Chat]:
    try:
        # query the chat
        chat = db.session.query(Chat).filter(Chat.id==chat_id).first()
        
        if not chat:
            return None
        
        # update the fields with the values from `update_data`
        for key, value in update_data.items():
            if hasattr(chat, key):
                setattr(chat, key, value)
                        
        # commit the changes
        db.session.commit()
        return chat.to_dict()
    except Exception as e:
        print(f"Error updating chat messages: {str(e)}")
        db.session.rollback()
        return None

def get_chat_repo(chat_id: str, user_id: str):
    try:
        chat = db.session.query(Chat).filter(
            and_(
                Chat.id == chat_id,
                Chat.user_id == user_id
            )
        ).first()
        chat_dict = chat.to_dict()
        return chat_dict

    except Exception as e:
        print(f"Error fetching chat: {str(e)}")
        return None
    
def get_user_chats_repo(current_user: str) -> Optional[List[Chat]]:
    try:
        chat = db.session.query(Chat).filter(Chat.user_id == current_user)
        chats = chat.all()
        messages_dict = [chat.to_dict() for chat in chats]
        return messages_dict
    except Exception as e:
        print(f"Error fetching chat: {str(e)}")
        return None

def generate_response(message, user, access_token, status_code):
    return jsonify({
        "message": message,
        "access_token": access_token,
        "user": user.to_dict(),
    }), status_code


@app.route("/auth", methods=["POST"])
def authentication():
    try:
        data = request.get_json()
        user_data = GoogleUserModel(**data)
        user = User.query.filter_by(email=user_data.email).first()
        if user:
            update_user_repo(user, user_data)
        else: 
            user = create_user_repo(user_data)
        access_token = generate_jwt(user)
        return generate_response("Signed in successfully", user, access_token, 200 if user else 201)
    
    except ValidationErr as e:
        print(f"An error occurred: {str(e)}")
        return jsonify({"message": "Failed to create user"}), 500
    except Exception as e:
        print(f"An error occurered: {str(e)}")
        return jsonify({"message": "An error occurred during sign in"}), 500

@app.route("/start-chat", methods=["POST"])
@jwt_required()
def create_chat():
    try:
        data = request.json
        messages = data.get("messages", [])
        current_user = get_jwt_identity() 
        new_message = Chat(user_id=current_user, messages=messages)
        db.session.add(new_message)
        db.session.commit()
        
        return jsonify({"message": "Chat created successfully", "chat_id": new_message.id}), 201
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify({"message": "An error occurred during sign in"}), 500
    
@app.route("/chats", methods=["GET"])
@jwt_required()
def get_current_user_chats():
    try:
        current_user = get_jwt_identity()
        messages = get_user_chats_repo(current_user)
        return jsonify(messages)
    except Exception as e:
        return jsonify({"error":f"Something went wrong {e}"})
    

@app.route("/chats/<string:chat_id>", methods=["GET"])
@jwt_required()
def get_chat(chat_id:str):
    try: 
        current_user_id = get_jwt_identity()
        chat = get_chat_repo(chat_id, current_user_id)
        if not chat:
            return jsonify({'error': 'Chat not found or not authorized'}), 404
        
        # Return the actual messages from the chat
        return jsonify(chat['messages']), 200
        
    except Exception as e:
        print(f"Error in get_chats: {str(e)}")
        return jsonify({
            "error": "An error occurred while fetching the chat"
        }), 500

@app.route("/chats/<string:chat_id>", methods=["PATCH"])
@jwt_required()
def update_chat(chat_id:str):
    try:
        data = request.get_json()
        current_user = get_jwt_identity()
        
        chat = get_chat_repo(chat_id=chat_id, user_id=current_user)
        if not chat:
            return jsonify({"error": "Chat not found"}), 404
        
        # Prepare the data for updaing - only update valid fields
        update_data = {}
        
        if "title" in data:
            update_data["title"] = data["title"]
        
        if "messages" in data:
            messages = data.get("messages", [])
            if not isinstance(messages, list):
                messages = [messages]
            update_data["messages"] = messages
        
        updated_chat = update_chat_repo(chat_id, current_user, update_data=update_data)
        if updated_chat:
            return jsonify(updated_chat), 200
        else:
            return jsonify({"error": "Chat not found or update failed"}), 404
    except Exception as e:
        print(f"Error in update_chat route: {str(e)}")
        return jsonify({"error": "An error occurred while updating the chat"}), 500
    
@app.route("/chats", methods=["POST"])
@jwt_required()
def chat():
    try:        
        messages = request.get_json().get("messages", [])
        if not isinstance(messages, list):
            messages = [messages]
        def generate():
            with app.app_context():  # Add this line
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
                        Chat.messages = messages
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