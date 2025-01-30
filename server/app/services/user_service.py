from app.repo.user_repo import UserRepository
from app.models.models import GoogleUserModel
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class UserService:
    @staticmethod
    def create_user(data: dict) -> tuple:
        """Create a new user or update existing user"""
        try:
            # Convert dict to GoogleUserModel
            user_data = GoogleUserModel(**data)
            # Create or update user
            return UserRepository.create_or_update_user(user_data)
        except Exception as e:
            print(f"Error in create_user service: {e}")
            raise

    @staticmethod
    def get_user_by_id(user_id):
        return UserRepository.get_user_by_id(user_id)
    
    @staticmethod
    def get_all_users():
        return UserRepository.get_all_users()
    
    @staticmethod
    def delete_user_by_id(user_id):
        UserRepository.delete_user_by_id(user_id)
        
    @staticmethod
    def update_user(user_id, username):
        UserRepository.update_user(user_id, username)