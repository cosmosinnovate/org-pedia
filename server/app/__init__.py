# app.__init__.py
from venv import logger
from flask import Flask, jsonify
from flask_cors import CORS
import logging
import os

from app.config import DevConfig, ProdConfig, TestConfig
from app.database.db import db, migrate, jwt, init_db

def create_app(config_name='default'):
    """Application factory function"""
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    app = Flask(__name__)
    
    # Load configuration
    config_class = {
        'development': DevConfig,
        'production': ProdConfig,
        'testing': TestConfig,
        'default': DevConfig
    }.get(config_name, DevConfig)
    
    app.config.from_object(config_class)
    config_class.init_app(app)

    # Initialize extensions
    db.init_app(app)
    app.config['ALEMBIC'] = {
        'script_location': 'migrations',
        'sqlalchemy.url': app.config['SQLALCHEMY_DATABASE_URI']
    }
    
    migrate.init_app(app, db)  # Initialize Flask-Migrate
    jwt.init_app(app)
    
    # Enable CORS
    CORS(app, supports_credentials=True)
    
    # Register blueprints
    from app.routes import (
        auth_bp,
        chat_history_bp   
    )

    # apis
    app.register_blueprint(auth_bp, url_prefix="/api/auth") 
    app.register_blueprint(chat_history_bp, url_prefix="/api/chats")

    @app.route("/")
    def health_check():
        return {"status": "ok"}

    # Error handling (remains synchronous for simplicity)
    @app.errorhandler(400)
    def bad_request(error):
        return {"error": "Bad request", "message": str(error)}, 400

    @app.errorhandler(404)
    def not_found(error):
        return {"error": "Not found", "message": str(error)}, 404

    @app.errorhandler(500)
    def internal_server_error(error):
        logger.error(f"Internal Server Error: {str(error)}")
        return {"error": "Internal server error", "message": "An unexpected error occurred"}, 500

    return app

# Create the app instance
app = create_app()
