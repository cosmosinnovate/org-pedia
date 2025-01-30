# tests/conftest.py
from app.database import db
import pytest
from app import create_app
import logging

logger = logging.getLogger(__name__)

@pytest.fixture
def app():
    logger.info("Creating test application")
    app = create_app()
    
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': 'test-key-please-ignore',
        'WTF_CSRF_ENABLED': False
    })
    
    # Log the configuration
    logger.info("Test application configuration: %s", app.config)
    
    with app.app_context():
        try:
            logger.info("Creating database tables")
            db.create_all()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error("Failed to create database tables: %s", str(e), exc_info=True)
            raise
        
        yield app
        logger.info("Cleaning up test database")
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    logger.info("Creating test client")
    return app.test_client()

@pytest.fixture
def runner(app):
    logger.info("Creating test CLI runner")
    return app.test_cli_runner()