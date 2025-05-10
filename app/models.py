# app/models.py
from . import db, bcrypt # db is the pymongo.database.Database instance
from flask_login import UserMixin
from . import login_manager
from bson import ObjectId # Required for querying by _id
from datetime import datetime, timedelta # Added timedelta
import secrets

@login_manager.user_loader
def load_user(user_id):
    user_data = db.users.find_one({"_id": ObjectId(user_id)})
    if (user_data):
        user = User() # __init__ sets _is_active_status to default True via is_active_param
        user.id = str(user_data["_id"])
        user.username = user_data["username"]
        user.email = user_data["email"]
        user.password_hash = user_data["password_hash"]
        user.role = user_data["role"]
        user.branch = user_data.get("branch")
        user.year = user_data.get("year")
        user.bio = user_data.get("bio")
        user.profile_photo = user_data.get("profile_photo")
        user.student_document = user_data.get("student_document")
        user.full_name = user_data.get("full_name")
        user.skills = user_data.get("skills", [])
        user.social_links = user_data.get("social_links", {})
        user.last_seen = user_data.get("last_seen")
        user.email_verified = user_data.get("email_verified", False) # New field
        user.email_verification_token = user_data.get("email_verification_token") # New field
        user.email_verification_token_expiry = user_data.get("email_verification_token_expiry") # New field
        user.password_reset_token = user_data.get("password_reset_token") # New field
        user.password_reset_token_expiry = user_data.get("password_reset_token_expiry") # New field
        user.is_active = user_data.get("is_active", True) # This will use the new setter
        user.is_admin = user_data.get("is_admin", False) # New field
        user.student_document_verified = user_data.get("student_document_verified", False) # New field
        return user
    return None

class User(UserMixin): # UserMixin provides is_authenticated, is_active, is_anonymous, get_id()
    def __init__(self, id=None, username=None, email=None, password_hash=None, role=None, branch=None, year=None, bio=None, profile_photo=None, student_document=None, full_name=None, skills=None, social_links=None, last_seen=None, email_verified=False, email_verification_token=None, email_verification_token_expiry=None, password_reset_token=None, password_reset_token_expiry=None, is_active_param=True, is_admin=False, student_document_verified=False): # Changed is_active to is_active_param
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.branch = branch
        self.year = year
        self.bio = bio
        self.profile_photo = profile_photo
        self.student_document = student_document
        self.full_name = full_name
        self.skills = skills or []  # Store as a list of skills
        self.social_links = social_links or {}  # Store as a dict e.g. {"github": "url", "linkedin": "url"}
        self.last_seen = last_seen
        self.email_verified = email_verified # New field
        self.email_verification_token = email_verification_token # New field
        self.email_verification_token_expiry = email_verification_token_expiry # New field
        self.password_reset_token = password_reset_token # New field
        self.password_reset_token_expiry = password_reset_token_expiry # New field
        self._is_active_status = is_active_param # Changed to internal attribute _is_active_status
        self.is_admin = is_admin # New field
        self.student_document_verified = student_document_verified # New field

    @property
    def is_active(self):
        return self._is_active_status

    @is_active.setter
    def is_active(self, value):
        self._is_active_status = bool(value)

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
            "bio": self.bio,
            "profile_photo": self.profile_photo,
            "student_document": self.student_document,
            "full_name": self.full_name,
            "skills": self.skills,
            "social_links": self.social_links,
            "last_seen": self.last_seen,
            "email_verified": self.email_verified, # New field
            "email_verification_token": self.email_verification_token, # New field
            "email_verification_token_expiry": self.email_verification_token_expiry, # New field
            "password_reset_token": self.password_reset_token, # New field
            "password_reset_token_expiry": self.password_reset_token_expiry, # New field
            "is_active": self._is_active_status, # Changed to save _is_active_status
            "is_admin": self.is_admin, # New field
            "student_document_verified": self.student_document_verified # New field
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
            # Ensure all fields are passed to the constructor
            return User(
                id=str(user_data['_id']),
                username=user_data.get('username'),
                email=user_data.get('email'),
                password_hash=user_data.get('password_hash'),
                role=user_data.get('role'),
                branch=user_data.get('branch'),
                year=user_data.get('year'),
                bio=user_data.get('bio'),
                profile_photo=user_data.get('profile_photo'),
                student_document=user_data.get('student_document'),
                full_name=user_data.get('full_name'),
                skills=user_data.get('skills', []),
                social_links=user_data.get('social_links', {}),
                last_seen=user_data.get('last_seen'),
                email_verified=user_data.get('email_verified', False),
                email_verification_token=user_data.get('email_verification_token'),
                email_verification_token_expiry=user_data.get('email_verification_token_expiry'),
                password_reset_token=user_data.get('password_reset_token'), # New field
                password_reset_token_expiry=user_data.get('password_reset_token_expiry'), # New field
                is_active_param=user_data.get('is_active', True), # Changed to is_active_param
                is_admin=user_data.get('is_admin', False), # New field
                student_document_verified=user_data.get('student_document_verified', False) # New field
            )
        return None

    @staticmethod
    def find_by_email(email):
        user_data = db.users.find_one({"email": email})
        if user_data:
            # Ensure all fields are passed to the constructor
            return User(
                id=str(user_data['_id']),
                username=user_data.get('username'),
                email=user_data.get('email'),
                password_hash=user_data.get('password_hash'),
                role=user_data.get('role'),
                branch=user_data.get('branch'),
                year=user_data.get('year'),
                bio=user_data.get('bio'),
                profile_photo=user_data.get('profile_photo'),
                student_document=user_data.get('student_document'),
                full_name=user_data.get('full_name'),
                skills=user_data.get('skills', []),
                social_links=user_data.get('social_links', {}),
                last_seen=user_data.get('last_seen'),
                email_verified=user_data.get('email_verified', False),
                email_verification_token=user_data.get('email_verification_token'),
                email_verification_token_expiry=user_data.get('email_verification_token_expiry'),
                password_reset_token=user_data.get('password_reset_token'), # New field
                password_reset_token_expiry=user_data.get('password_reset_token_expiry'), # New field
                is_active_param=user_data.get('is_active', True), # Changed to is_active_param
                is_admin=user_data.get('is_admin', False), # New field
                student_document_verified=user_data.get('student_document_verified', False) # New field
            )
        return None

    @staticmethod
    def find_by_verification_token(token):
        user_data = db.users.find_one({"email_verification_token": token})
        if user_data:
            # Ensure all fields are passed to the constructor
            return User(
                id=str(user_data['_id']),
                username=user_data.get('username'),
                email=user_data.get('email'),
                password_hash=user_data.get('password_hash'),
                role=user_data.get('role'),
                branch=user_data.get('branch'),
                year=user_data.get('year'),
                bio=user_data.get('bio'),
                profile_photo=user_data.get('profile_photo'),
                student_document=user_data.get('student_document'),
                full_name=user_data.get('full_name'),
                skills=user_data.get('skills', []),
                social_links=user_data.get('social_links', {}),
                last_seen=user_data.get('last_seen'),
                email_verified=user_data.get('email_verified', False),
                email_verification_token=user_data.get('email_verification_token'),
                email_verification_token_expiry=user_data.get('email_verification_token_expiry'),
                password_reset_token=user_data.get('password_reset_token'), # New field
                password_reset_token_expiry=user_data.get('password_reset_token_expiry'), # New field
                is_active_param=user_data.get('is_active', True), # Changed to is_active_param
                is_admin=user_data.get('is_admin', False), # New field
                student_document_verified=user_data.get('student_document_verified', False) # New field
            )
        return None

    @staticmethod
    def find_by_password_reset_token(token): # New method
        user_data = db.users.find_one({"password_reset_token": token})
        if user_data:
            return User(
                id=str(user_data['_id']),
                username=user_data.get('username'),
                email=user_data.get('email'),
                password_hash=user_data.get('password_hash'),
                role=user_data.get('role'),
                branch=user_data.get('branch'),
                year=user_data.get('year'),
                bio=user_data.get('bio'),
                profile_photo=user_data.get('profile_photo'),
                student_document=user_data.get('student_document'),
                full_name=user_data.get('full_name'),
                skills=user_data.get('skills', []),
                social_links=user_data.get('social_links', {}),
                last_seen=user_data.get('last_seen'),
                email_verified=user_data.get('email_verified', False),
                email_verification_token=user_data.get('email_verification_token'),
                email_verification_token_expiry=user_data.get('email_verification_token_expiry'),
                password_reset_token=user_data.get('password_reset_token'),
                password_reset_token_expiry=user_data.get('password_reset_token_expiry'),
                is_active_param=user_data.get('is_active', True), # Changed to is_active_param
                is_admin=user_data.get('is_admin', False), # New field
                student_document_verified=user_data.get('student_document_verified', False) # New field
            )
        return None

    def generate_email_verification_token(self):
        self.email_verification_token = secrets.token_urlsafe(32)
        self.email_verification_token_expiry = datetime.utcnow() + timedelta(hours=24) # Token valid for 24 hours
        self.save()
        return self.email_verification_token

    def verify_email_token(self, token):
        if self.email_verification_token == token and self.email_verification_token_expiry > datetime.utcnow():
            self.email_verified = True
            self.email_verification_token = None # Clear token after use
            self.email_verification_token_expiry = None
            self.save()
            return True
        return False

    def generate_password_reset_token(self): # New method
        self.password_reset_token = secrets.token_urlsafe(32)
        self.password_reset_token_expiry = datetime.utcnow() + timedelta(hours=1) # Token valid for 1 hour
        self.save()
        return self.password_reset_token

    def verify_password_reset_token(self, token): # New method
        if self.password_reset_token == token and self.password_reset_token_expiry > datetime.utcnow():
            return True
        return False

    @staticmethod
    def find_all(query_filter=None):
        """Finds all users, optionally applying a filter."""
        if query_filter is None:
            query_filter = {}
        users_cursor = db.users.find(query_filter)
        users_list = []
        for user_data in users_cursor:
            users_list.append(User(
                id=str(user_data['_id']),
                username=user_data.get('username'),
                email=user_data.get('email'),
                password_hash=user_data.get('password_hash'),
                role=user_data.get('role'),
                branch=user_data.get('branch'),
                year=user_data.get('year'),
                bio=user_data.get('bio'),
                profile_photo=user_data.get('profile_photo'),
                student_document=user_data.get('student_document'),
                full_name=user_data.get('full_name'),
                skills=user_data.get('skills', []),
                social_links=user_data.get('social_links', {}),
                last_seen=user_data.get('last_seen'),
                email_verified=user_data.get('email_verified', False),
                email_verification_token=user_data.get('email_verification_token'),
                email_verification_token_expiry=user_data.get('email_verification_token_expiry'),
                password_reset_token=user_data.get('password_reset_token'),
                password_reset_token_expiry=user_data.get('password_reset_token_expiry'),
                is_active_param=user_data.get('is_active', True),
                is_admin=user_data.get('is_admin', False),
                student_document_verified=user_data.get('student_document_verified', False)
            ))
        return users_list

    @staticmethod
    def find_by_role(role):
        return User.find_all({"role": role})

    @staticmethod
    def find_by_branch(branch):
        return User.find_all({"branch": branch})

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
        "room": room_name,
        "read_at": None  # New field for read receipts
    }
    result = db.messages.insert_one(message_data)
    # Return the full message document including the new _id and other fields
    return db.messages.find_one({"_id": result.inserted_id})

def get_messages_for_room(room_name, limit=50):
    messages_cursor = db.messages.find({"room": room_name}).sort("timestamp", -1).limit(limit)
    messages_list = []
    for msg in messages_cursor:
        msg['_id'] = str(msg['_id']) # Convert ObjectId to string
        if 'sender_id' in msg and isinstance(msg['sender_id'], ObjectId):
            msg['sender_id'] = str(msg['sender_id'])
        if 'receiver_id' in msg and isinstance(msg['receiver_id'], ObjectId):
            msg['receiver_id'] = str(msg['receiver_id'])
        # Ensure read_at is included, it should be already by find()
        messages_list.append(msg)
    return messages_list # Returns a list of dicts

def mark_message_as_read(message_id: str, reader_username: str):
    """Marks a message as read by the reader if they are the recipient and it's not already read."""
    try:
        msg_object_id = ObjectId(message_id)
    except Exception:
        return None # Invalid message_id format

    message = db.messages.find_one({"_id": msg_object_id})

    if not message:
        return None # Message not found

    # Check if the reader is the intended recipient and the message hasn't been read yet
    if message.get('receiver_username') == reader_username and message.get('read_at') is None:
        current_time = datetime.utcnow()
        result = db.messages.update_one(
            {"_id": msg_object_id},
            {"$set": {"read_at": current_time}}
        )
        if result.modified_count > 0:
            # Return the updated information
            return {
                "_id": message_id, # Return as string
                "read_at": current_time,
                "sender_username": message.get('sender_username'),
                "receiver_username": message.get('receiver_username'), # who read it
                "room": message.get("room")
            }
    return None # Not updated (either not recipient, or already read, or DB error)
