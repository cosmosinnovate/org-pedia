from datetime import datetime
from app.repo.chat_repo import ChatHistoryRepository as chat_repo
import logging

logger = logging.getLogger(__name__)

class ChatHistoryService:
    @staticmethod
    def create_chat_message(user_id, title, messages):
        """
        Create a new chat message.
        
        Args:
            user_id (str): ID of the user creating the chat
            title (str): Title of the chat
            messages (list): List of message dictionaries with 'role' and 'content'
            
        Returns:
            bool: True if message was saved successfully
        """
        logger.info(f"Saving chat message for user: {user_id}")
        chat_repo.save_chat_to_db(
            user_id=user_id,
            title=title,
            messages=messages,
        )
        
        logger.info(f"Chat message saved for user: {user_id}")
        return True
        
    @staticmethod
    def get_user_chat_by_id(user_id):
        """Get all chats for a user"""
        logger.info(f"Fetching chat history for user: {user_id}")
        return chat_repo.get_user_chat_by_id(user_id)
        
    @staticmethod
    def get_chat_history_by_id(chat_id, user_id):
        """Get a specific chat by ID"""
        logger.info(f"Fetching chat history with id: {chat_id} for user: {user_id}")
        return chat_repo.get_chat_history_by_id(chat_id, user_id)

    @staticmethod
    def _get_current_timestamp():
        """Get current timestamp in ISO format"""
        logger.info("Getting current timestamp")
        return datetime.now().isoformat()