
from app.repo.user_repo import UserRepository as user_repo

class UserService:
    @staticmethod
    def create_user(user_data:dict):
        return user_repo.save_user_to_db(user_data)
        
    @staticmethod
    def get_user_by_id(user_id):
        return user_repo.get_user_by_id(user_id)
    
    @staticmethod
    def get_all_users():
        return user_repo.get_all_users()
    
    @staticmethod
    def delete_user_by_id(user_id):
        user_repo.delete_user_by_id(user_id)
        
    @staticmethod
    def update_user(user_id, username):
        user_repo.update_user(user_id, username)
        