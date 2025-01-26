# app.__init__.py
from venv import logger
from flask import Flask
import os
from flask_cors import CORS

from app.config import DevConfig, ProdConfig, TestConfig
from flask_cors import CORS

from app.database.db import db, migrate, jwt

# Flask app initialization
app = Flask(__name__)
CORS(app)

def create_app(config_name=None):
    app = Flask(__name__)
    CORS(app, supports_credentials=True)
    
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
        
    config_mapping = {
        "development": DevConfig,
        "production": ProdConfig,
        "testing": TestConfig,
        None: DevConfig,  # Default to development
    }

    # Get config class and handle invalid config names
    config_class = config_mapping.get(config_name)
    if config_class is None:
        app.logger.warning(
            f"Invalid config name '{config_name}'. Defaulting to development."
        )
        config_class = DevConfig

    # Apply configuration
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
    # init_migration_cli(app)  # This adds the 'flask safe-migrate' command

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

    # Register blueprints
    from app.routes import (
        auth_bp,
        chat_history_bp   
        )

    # apis
    app.register_blueprint(auth_bp, url_prefix="/api/auth") 
    app.register_blueprint(chat_history_bp, url_prefix="/api/business")

    
    return app
