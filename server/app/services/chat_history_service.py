from datetime import datetime
from app.repo.chat_repo import ChatHistoryRepository as chat_repo

class ChatHistoryService:
    @staticmethod
    def create_chat_message(user_id,title, message):
        chat_repo.save_chat_to_db(
            user_id=user_id,
            title=title,
            message=message,
        )
        
        
    @staticmethod
    def get_user_chat_by_id(user_id):
        return chat_repo.get_user_chat_by_id(user_id)
        
    @staticmethod
    def get_chat_history_by_id(self, chat_id, user_id):
        return chat_repo.get_chat_history_by_id(chat_id, user_id)

    @staticmethod
    def _get_current_timestamp(self):
        return datetime.now().isoformat()