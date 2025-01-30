# app/routes/__init__.py
from flask import Blueprint
from .auth_routes import auth_bp
from .chat_routes import chat_history_bp

__all__ = [
    'auth_bp',
    'chat_history_bp',
]