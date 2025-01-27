from app.models.models import ChatHistory as Chat
from sqlite3 import OperationalError
from app.database.db import db
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ChatHistoryRepository:
    @staticmethod
    def save_chat_to_db(user_id, title, messages):
        """
        Save a chat to the database.
        
        Args:
            user_id (str): ID of the user creating the chat
            title (str): Title of the chat
            messages (list): List of message dictionaries with 'role' and 'content'
        """
        try:
            chat = Chat(
                user_id=user_id, 
                title=title, 
                messages=messages
            )
            db.session.add(chat)
            db.session.commit()
            logger.info(f"Chat saved successfully for user: {user_id}")
        except Exception as e:
            logger.error(f"Error saving chat: {str(e)}")
            db.session.rollback()
            raise
        
    @staticmethod
    def get_chat_history_by_id(chat_id, user_id):
        """Get a specific chat by ID"""
        try:
            chat = Chat.query.filter_by(id=chat_id, user_id=user_id).first()
            return chat.to_dict() if chat else None
        except Exception as e:
            logger.error(f"Error fetching chat: {str(e)}")
            return None
        
    @staticmethod
    def get_all_chats():
        """Get all chats"""
        chats = Chat.query.all()
        return [chat.to_dict() for chat in chats]
    
    @staticmethod
    def get_user_chat_by_id(user_id):
        """Get all chats for a user"""
        try:
            chats = Chat.query.filter_by(user_id=user_id).order_by(Chat.created_at.desc()).all()
            return [chat.to_dict() for chat in chats]
        except Exception as e:
            logger.error(f"Error fetching user chats: {str(e)}")
            return []
    
    @staticmethod
    def delete_chat_by_id(chat_id):
        try:
            chat = Chat.query.filter_by(id=chat_id).first()
            db.session.delete(chat)
            db.session.commit()
        except Exception as e:
            print(f"Error deleting chat: {e}")
            raise
        
    @staticmethod
    def update_chat(chat_id, title, messages):
        try:
            chat = Chat.query.filter_by(id=chat_id).first()
            chat.title = title
            chat.messages = messages
            db.session.commit()
        except Exception as e:
            print(f"Error updating chat: {e}")
            raise
        
    @staticmethod
    def delete_chats_by_user_id(user_id):
        try:            
            Chat.query.filter_by(user_id=user_id).delete()
            db.session.commit()
        except Exception as e:
            print(f"Error deleting chats: {e}")
            raise
