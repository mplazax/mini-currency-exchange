"""
Application initialization
"""
from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
import logging

from app.config.config import get_config
from app.models.user import User
from app.services.database import DatabaseService

# Routes
from app.routes.auth_routes import auth_bp
from app.routes.offer_routes import offer_bp
from app.routes.user_routes import user_bp

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

login_manager = LoginManager()


def create_app(config_name='default'):
    """
    Create Flask application
    
    Args:
        config_name: Configuration environment
        
    Returns:
        Flask application
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(get_config())
    
    # Set up CORS
    CORS(app, supports_credentials=True)
    
    # Initialize login manager
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(offer_bp)
    app.register_blueprint(user_bp)
    
    # Initialize database connection
    db_service = DatabaseService()
    
    # Setup login manager user loader
    @login_manager.user_loader
    def load_user(user_id):
        user_record = db_service.get_user_by_id(user_id)
        if user_record:
            return User(
                user_id=str(user_record['_id']),
                email=user_record['email'],
                name=user_record.get('name')
            )
        return None
    
    return app 