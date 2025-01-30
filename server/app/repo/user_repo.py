from datetime import datetime
from sqlite3 import OperationalError
import logging

from app.database.db import db
from app.utils import generate_jwt
from app.models.models import UserModel

logger = logging.getLogger(__name__)

class UserRepository:
    @staticmethod
    def create_or_update_user(user_data):
        """
        Create or update a user in the database.
        
        Args:
            user_data (dict): A dictionary containing the user data.
        
        Returns:
            tuple: A tuple containing the user object and the access token.
        
        Raises:
            Exception: If there is an error creating or updating the user.
        """
        logger.info(f"Creating or updating user with email: {user_data.email}")
        try:
            # Check if user exists
            user = UserModel.query.filter_by(email=user_data.email).first()
            
            if user:
                # Existing user, update user data
                user.display_name = user_data.display_name
                user.email = user_data.email
                user.photo_url = user_data.photo_url
                user.access_token = user_data.access_token
                user.updated_at = datetime.now()
                db.session.commit()
                logger.info(f"Updated existing user: {user.email}")
            else:
                # New user, create and save user data
                user = UserModel(
                    display_name=user_data.display_name,
                    email=user_data.email,
                    photo_url=user_data.photo_url,
                    access_token=user_data.access_token
                )
                db.session.add(user)
                logger.info(f"Created new user: {user.email}")
            
            # Commit the changes
            db.session.commit()
            
            # Generate JWT token
            access_token = generate_jwt(user)
            return user, access_token
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error saving user: {str(e)}")
            raise

    @staticmethod
    def get_user_by_email(email: str):
        try:
            return UserModel.query.filter_by(email=email).first()
        except Exception as e:
            logger.error(f"Error fetching user: {str(e)}")
            return None

    @staticmethod
    def get_user_by_id(user_id):
        try:
            return UserModel.query.filter_by(id=user_id).first()
        except Exception as e:
            logger.error(f"Error fetching user: {str(e)}")
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
            logger.error(f"Error deleting user: {str(e)}")
            raise

    @staticmethod
    def update_user(user_id, username):
        try:
            user = UserModel.query.filter_by(id=user_id).first()
            user.username = username
            db.session.commit()
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            raise
