from sqlite3 import OperationalError

from app.database import db
from app.utils import generate_jwt

from app.models.models import GoogleUserModel, User as UserModel


class UserRepository:
    @staticmethod
    def save_user_to_db(data: dict)-> tuple:
        try:
            user_data = GoogleUserModel(**data)
            # Check if user already exists
            user = UserRepository.get_user_by_email(email=user_data.email)
            
            if user:
                # Existing user, update user data
                UserRepository.update_user_repo(user, user_data)
            else:
                # New user, save user data
                user = UserModel(
                    user_google_id=user_data.user_google_id,
                    display_name=user_data.display_name,
                    email=user_data.email,
                    photo_url=user_data.photo_url,
                    access_token=user_data.access_token,
                )
                db.session.add(user)
                db.session.commit()
            # Generate JWT token
            access_token = generate_jwt(user)
            return user, access_token
        
        except OperationalError as e:
            print(f"Error saving user: {e}")
            raise

    @staticmethod
    def update_user_repo(user, user_data):
        user.username = user_data.username
        user.email = user_data.email
        user.photo_url = user_data.photo_url
        user.access_token = user_data.access_token
        db.session.commit()
        return user
    
    @staticmethod
    def get_user_by_email(email: str):
        try:
            return UserModel.query.filter_by(email=email).first()
        except Exception as e:
            print(f"Error fetching user: {e}")
            return None

    @staticmethod
    def get_user_by_id(user_id):
        try:
            return UserModel.query.filter_by(id=user_id).first()
        except Exception as e:
            print(f"Error fetching user: {e}")
            return None

    @staticmethod
    def get_all_users():
        return UserModel.query.all()

    @staticmethod
    def delete_user_by_id(user_id):
        try:
            user = UserModel.query.filter_by(id=user_id).first()
            db.session.delete(user)
            db.session.commit()
        except Exception as e:
            print(f"Error deleting user: {e}")
            raise

    @staticmethod
    def update_user(user_id, username):
        try:
            user = UserModel.query.filter_by(id=user_id).first()
            user.username = username
            db.session.commit()
        except Exception as e:
            print(f"Error updating user: {e}")
            raise
