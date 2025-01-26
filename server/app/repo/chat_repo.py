from app.models.models import ChatHistory as Chat
from sqlite3 import OperationalError
from app.database import db

class ChatHistoryRepository:
    @staticmethod
    def save_chat_to_db(user_id, title, messages, created_at):
        try:
            chat = Chat(user_id=user_id, title=title, messages=messages, created_at=created_at)
            db.session.add(chat)
            db.session.commit()
        except OperationalError as e:
            print(f"Error saving chat: {e}")
            raise
        
    @staticmethod
    def get_chat_history_by_id(chat_id, user_id):
        try:
            return Chat.query.filter_by(id=chat_id, user_id=user_id).first()
        except Exception as e:
            print(f"Error fetching chat: {e}")
            return None
        
    @staticmethod
    def get_all_chats():
        return Chat.query.all()
    
    @staticmethod
    def get_user_chat_by_id(user_id):
        return Chat.query.filter_by(user_id=user_id).all()
    
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
        
