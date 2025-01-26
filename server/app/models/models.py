from datetime import datetime, timezone
from uuid import uuid4
from pydantic import BaseModel
from sqlalchemy import Column, ForeignKey, String,JSON, DateTime
from app import db

# Define a Pydantic model for the incoming user data
class GoogleUserModel(BaseModel):
    user_google_id: str
    display_name: str
    email: str
    photo_url: str
    access_token: str
    
class User(db.Model):
    __tablename__ = "users"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    display_name = Column(String, index=True)
    user_google_id = Column(String)
    email = Column(String, unique=True, index=True)
    photo_url = Column(String)
    access_token = Column(String)

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
        
class ChatHistory(db.Model):
    __tablename__ = "chat_history"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    title = Column(String, index=True, nullable=False)
    messages = Column(JSON)
    created_at = Column(DateTime, index=True, default=lambda: datetime.now(timezone.utc))
    
    def __init__(self, user_id=None, title=None, messages=None):
        self.user_id = user_id
        self.title = title
        self.messages = messages
    
    def __repr__(self):
        return f"Message(id={self.id}, id={self.id}, title={self.title} messages='{str(self.messages)[:20]}...')"
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "messages": self.messages,
        }
        
        