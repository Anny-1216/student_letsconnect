# app/__init__.py

import os
from flask import Flask, redirect, url_for, jsonify # Added jsonify
from flask_socketio import SocketIO
from flask_login import LoginManager, current_user
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from pymongo import MongoClient
from flask_wtf.csrf import CSRFProtect, CSRFError # Import CSRFError
from flask_mail import Mail # Import Mail
from werkzeug.middleware.proxy_fix import ProxyFix # Import ProxyFix

# Initialize extensions
socketio = SocketIO()
login_manager = LoginManager()
bcrypt = Bcrypt()
jwt = JWTManager()
csrf = CSRFProtect() # Initialize CSRFProtect instance
mail = Mail() # Initialize Mail instance

# MongoDB client (replace with your connection string if needed)
client = MongoClient("MONGO_URI",'mongodb://localhost:27017/')
db = client.lets_connect_db

def create_app():
    app = Flask(__name__)
    
    # Apply ProxyFix to handle headers from ngrok (or other reverse proxies)
    # This should be done early, before other app configurations if they depend on URL generation
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_secret_key_placeholder')  # Change this!
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'your_jwt_secret_key_placeholder') # Change this!
    app.config['MONGO_URI'] = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/letsconnect')
    
    # Email configuration
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = 'chaitanyapaigude1204@gmail.com'
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'your_mail_password_placeholder')
    app.config['MAIL_DEFAULT_SENDER'] = 'chaitanyapaigude1204@gmail.com'

    # It's good practice to also set WTF_CSRF_ENABLED, though it's often true by default.
    # app.config['WTF_CSRF_ENABLED'] = True 

    # Initialize extensions with app
    socketio.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app) # bcrypt is initialized here
    jwt.init_app(app)
    csrf.init_app(app) # Initialize CSRFProtect with the app
    mail.init_app(app) # Initialize Mail with the app

    # Login manager configuration
    login_manager.login_view = 'auth.login' # Blueprint name 'auth', route 'login'
    login_manager.login_message_category = 'info'

    # Import models for context processor AFTER db and bcrypt are initialized
    from .models import User, get_connection_status_between_users

    # Custom CSRF error handler
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return jsonify(error=e.description, details="CSRF validation failed."), 400

    # Context processors to make functions available in all templates
    @app.context_processor
    def utility_processor():
        def get_conn_status(user1_id, user2_id):
            # Wrapper to ensure current_user is handled correctly if one of them is current_user
            # And to handle potential None for user2_id if the user object doesn't exist
            if not user1_id or not user2_id:
                return "none"
            return get_connection_status_between_users(user1_id, user2_id)
        
        from .models import get_unread_message_count  # Import here to avoid circular imports
        
        print("Utility processor executed: get_unread_message_count is available")
        
        return dict(
            get_connection_status_between_users=get_conn_status,
            get_unread_message_count=get_unread_message_count,  # Add this function
            User=User
        )

    # Import and register blueprints
    from .auth import auth_bp
    from .chat import chat_bp
    from .matchmaking import matchmaking_bp
    from .main_routes import main_bp
    from .admin import admin_bp # Import admin blueprint
    from .connections import connections_bp # Import connections blueprint
    # Import socket events to register them
    from . import socket_events

    app.register_blueprint(main_bp)  # No url_prefix for main routes
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(chat_bp, url_prefix='/chat')
    app.register_blueprint(matchmaking_bp, url_prefix='/matchmaking')
    app.register_blueprint(admin_bp) # Register admin blueprint (already has prefix)
    app.register_blueprint(connections_bp, url_prefix='/connections') # Register connections blueprint

    # Root route is now handled by main_bp

    return app
