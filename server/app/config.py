import os
import pathlib
from dotenv import load_dotenv
from datetime import timedelta
import logging.config

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

# Create logs directory
def ensure_logs_directory():
    log_dir = os.path.join(os.path.dirname(basedir), 'logs')
    pathlib.Path(log_dir).mkdir(parents=True, exist_ok=True)
    return log_dir

# Environment check
FLASK_ENV = os.environ.get('FLASK_ENV', 'development')

# Database credentials
DATABASE_USERNAME = os.environ.get('DATABASE_USERNAME')
DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD')
DATABASE_HOST = os.environ.get('DATABASE_HOST')
DATABASE_HOST_PORT = os.environ.get('DATABASE_HOST_PORT')
DATABASE_NAME = os.environ.get('DATABASE_NAME')

# Validate environment variables
def validate_env_vars(env_vars, config_name):
    missing_vars = [var for var, value in env_vars.items() if not value]
    if missing_vars:
        raise ValueError(
            f"Missing required environment variables for {config_name}: "
            f"{', '.join(missing_vars)}"
        )

class Config:
    """Base config."""
    # JWT configuration
    SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@"
        f"{DATABASE_HOST}:{DATABASE_HOST_PORT}/{DATABASE_NAME}"
    )
    
    # SendGrid configuration
    SENDGRID_FROM_EMAIL = os.environ.get('SENDGRID_FROM_EMAIL')
    SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # RQ configuration
    RQ_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    RQ_QUEUES = ['default', 'high', 'low', 'email']
    RQ_ASYNC = os.environ.get('RQ_ASYNC', 'True').lower() == 'true'

    @staticmethod
    def configure_logging():
        log_dir = ensure_logs_directory()
        log_file = os.path.join(log_dir, 'app.log')

        LOGGING_CONFIG = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'default': {
                    'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
                },
                'detailed': {
                    'format': '[%(asctime)s] %(levelname)s in %(module)s [%(pathname)s:%(lineno)d]:\n%(message)s'
                }
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'formatter': 'default',
                    'stream': 'ext://sys.stdout'
                }
            },
            'root': {
                'level': 'INFO',
                'handlers': ['console']
            }
        }

        # Only add file handler if we can write to the logs directory
        try:
            # Test if we can write to the log file
            with open(log_file, 'a') as f:
                pass
            
            LOGGING_CONFIG['handlers']['file'] = {
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'detailed',
                'filename': log_file,
                'maxBytes': 1024 * 1024,  # 1MB
                'backupCount': 10
            }
            LOGGING_CONFIG['root']['handlers'].append('file')
        except OSError as e:
            print(f"Warning: Could not set up file logging: {e}")

        try:
            logging.config.dictConfig(LOGGING_CONFIG)
        except (ValueError, TypeError, AttributeError, ImportError) as e:
            # Fallback to basic logging configuration
            logging.basicConfig(
                level=logging.INFO,
                format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
            )
            logging.warning(f"Could not configure logging: {e}")

    @classmethod
    def init_app(cls, app):
        cls.configure_logging()
        
        # Add application-specific logging
        if not app.debug and not app.testing:
            # Set app logger level
            app.logger.setLevel(logging.INFO)
            
            # Ensure all handlers have the right formatter
            for handler in app.logger.handlers:
                handler.setFormatter(logging.Formatter(
                    '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
                ))     

class ProdConfig(Config):
    """Production config."""
    ENV = 'production'
    DEBUG = False
    
    def __init__(self):
        # Production-specific required variables
        prod_vars = {
            'SECRET_KEY': os.environ.get('SECRET_KEY'),
            'JWT_SECRET_KEY': os.environ.get('JWT_SECRET_KEY'),
            'DATABASE_URL': os.environ.get('DATABASE_URL'),
            'SENDGRID_API_KEY'  : os.environ.get('SENDGRID_API_KEY'),
            # 'REDIS_URL': os.environ.get('REDIS_URL')
        }
        validate_env_vars(prod_vars, 'Production')
        
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        # Production specific setup
        import logging
        from logging.handlers import RotatingFileHandler
        
        # File handler
        file_handler = RotatingFileHandler(
            'logs/application.log',
            maxBytes=10240,
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        # Log level
        app.logger.setLevel(logging.INFO)
        app.logger.info('Application startup')

class DevConfig(Config):
    """Development config."""
    ENV = 'development'
    DEBUG = True
    
    def __init__(self):
        # Development-specific required variables
        dev_vars = {
            'DATABASE_USERNAME': DATABASE_USERNAME,
            'DATABASE_PASSWORD': DATABASE_PASSWORD,
            'DATABASE_HOST': DATABASE_HOST,
            'DATABASE_NAME': DATABASE_NAME
        }
        validate_env_vars(dev_vars, 'Development')

class TestConfig(Config):
    """Testing config."""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

    def __init__(self):
        # Test-specific configuration
        pass