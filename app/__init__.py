# app/__init__.py

from flask import Flask
from flask_socketio import SocketIO
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from pymongo import MongoClient

# Initialize extensions
socketio = SocketIO()
login_manager = LoginManager()
bcrypt = Bcrypt()
jwt = JWTManager()

# MongoDB client (replace with your connection string if needed)
client = MongoClient('mongodb://localhost:27017/')
db = client.lets_connect_db

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key'  # Change this!
    app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key' # Change this!

    # Initialize extensions with app
    socketio.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # Login manager configuration
    login_manager.login_view = 'auth.login' # Blueprint name 'auth', route 'login'
    login_manager.login_message_category = 'info'

    # Import and register blueprints
    from .auth import auth_bp
    from .chat import chat_bp
    from .matchmaking import matchmaking_bp
    # Import socket events to register them
    from . import socket_events

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(chat_bp, url_prefix='/chat')
    app.register_blueprint(matchmaking_bp, url_prefix='/matchmaking')

    return app