# app/models.py
from . import db, bcrypt # db is the pymongo.database.Database instance
from flask_login import UserMixin
from . import login_manager
from bson import ObjectId # Required for querying by _id
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    user_data = db.users.find_one({"_id": ObjectId(user_id)})
    if user_data:
        user = User()
        user.id = str(user_data["_id"])
        user.username = user_data["username"]
        user.email = user_data["email"]
        user.password_hash = user_data["password_hash"]
        user.role = user_data["role"]
        user.branch = user_data.get("branch")
        user.year = user_data.get("year")
        user.bio = user_data.get("bio")
        return user
    return None

class User(UserMixin): # UserMixin provides is_authenticated, is_active, is_anonymous, get_id()
    def __init__(self, id=None, username=None, email=None, password_hash=None, role=None, branch=None, year=None, bio=None):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.branch = branch
        self.year = year
        self.bio = bio

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def save(self):
        """Saves or updates the user in the database."""
        user_data = {
            "username": self.username,
            "email": self.email,
            "password_hash": self.password_hash,
            "role": self.role,
            "branch": self.branch,
            "year": self.year,
            "bio": self.bio
        }
        if self.id: # Update existing user
            db.users.update_one({"_id": ObjectId(self.id)}, {"$set": user_data})
        else: # Insert new user
            result = db.users.insert_one(user_data)
            self.id = str(result.inserted_id)
        return self.id

    @staticmethod
    def find_by_username(username):
        user_data = db.users.find_one({"username": username})
        if user_data:
            return User(**{k:v for k,v in user_data.items() if k != '_id'}, id=str(user_data['_id']))
        return None

    @staticmethod
    def find_by_email(email):
        user_data = db.users.find_one({"email": email})
        if user_data:
            return User(**{k:v for k,v in user_data.items() if k != '_id'}, id=str(user_data['_id']))
        return None

# Example of how you might structure Message saving, though not a full class model here
def save_message(sender_username, receiver_username, content, room_name):
    sender = User.find_by_username(sender_username)
    receiver = User.find_by_username(receiver_username)

    if not sender or not receiver:
        # Handle error: user not found
        return None

    message_data = {
        "sender_id": ObjectId(sender.id),
        "receiver_id": ObjectId(receiver.id),
        "sender_username": sender_username, # Denormalize for easier display
        "receiver_username": receiver_username, # Denormalize for easier display
        "content": content,
        "timestamp": datetime.utcnow(),
        "room": room_name
    }
    result = db.messages.insert_one(message_data)
    return result.inserted_id

def get_messages_for_room(room_name, limit=50):
    messages_cursor = db.messages.find({"room": room_name}).sort("timestamp", -1).limit(limit)
    return list(messages_cursor) # Returns a list of dicts
