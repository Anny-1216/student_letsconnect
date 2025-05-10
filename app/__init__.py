# app/__init__.py

from flask import Flask, redirect, url_for
from flask_socketio import SocketIO
from flask_login import LoginManager, current_user
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from pymongo import MongoClient
from flask_wtf.csrf import CSRFProtect # Import CSRFProtect
from flask_mail import Mail # Import Mail

# Initialize extensions
socketio = SocketIO()
login_manager = LoginManager()
bcrypt = Bcrypt()
jwt = JWTManager()
csrf = CSRFProtect() # Initialize CSRFProtect instance
mail = Mail() # Initialize Mail instance

# MongoDB client (replace with your connection string if needed)
client = MongoClient('mongodb://localhost:27017/')
db = client.lets_connect_db

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key'  # Change this!
    app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key' # Change this!
    # Flask-Mail configuration - replace with your actual email server details
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = 'chaitanyapaigude1204@gmail.com'
    app.config['MAIL_PASSWORD'] = 'wvzzqiebhyipqxrl'
    app.config['MAIL_DEFAULT_SENDER'] = 'chaitanyapaigude1204@gmail.com'

    # It's good practice to also set WTF_CSRF_ENABLED, though it's often true by default.
    # app.config['WTF_CSRF_ENABLED'] = True 

    # Initialize extensions with app
    socketio.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    csrf.init_app(app) # Initialize CSRFProtect with the app
    mail.init_app(app) # Initialize Mail with the app

    # Login manager configuration
    login_manager.login_view = 'auth.login' # Blueprint name 'auth', route 'login'
    login_manager.login_message_category = 'info'

    # Import and register blueprints
    from .auth import auth_bp
    from .chat import chat_bp
    from .matchmaking import matchmaking_bp
    from .main_routes import main_bp
    from .admin import admin_bp # Import admin blueprint
    # Import socket events to register them
    from . import socket_events

    app.register_blueprint(main_bp)  # No url_prefix for main routes
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(chat_bp, url_prefix='/chat')
    app.register_blueprint(matchmaking_bp, url_prefix='/matchmaking')
    app.register_blueprint(admin_bp) # Register admin blueprint (already has prefix)

    # Root route is now handled by main_bp

    return app