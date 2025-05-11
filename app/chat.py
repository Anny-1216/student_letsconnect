# app/chat.py
import os
from flask import Blueprint, render_template, redirect, url_for, request, current_app, jsonify, flash # Added flash
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from .models import User, get_messages_for_room, are_users_connected, mark_all_messages_as_read_in_room # Added mark_all_messages_as_read_in_room
from .socket_events import get_room_name # Import the get_room_name function

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'mp4', 'webm', 'ogg'}
UPLOAD_FOLDER = 'chat_files' # Relative to static folder

chat_bp = Blueprint('chat', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@chat_bp.route('/with/<target_username>', methods=['GET'])
@login_required
def start_chat_page(target_username):
    target_user = User.find_by_username(target_username)
    if not target_user:
        # Handle user not found, perhaps flash a message and redirect
        flash('User not found.', 'danger')
        return redirect(url_for('matchmaking.browse_users')) # Or some error page

    if target_user.username == current_user.username:
        # Prevent user from chatting with themselves
        flash('You cannot chat with yourself.', 'warning')
        return redirect(url_for('matchmaking.browse_users'))

    # Check if users are connected before allowing chat
    if not are_users_connected(current_user.id, target_user.id):
        flash(f'You must be connected with {target_user.username} to chat.', 'warning')
        # Redirect to the target user's profile or browse page
        # If you have a profile page: url_for('auth.profile', username=target_user.username)
        return redirect(url_for('matchmaking.browse_users'))

    # Determine the room name using the same logic as in socket_events
    # Ensure this is consistent with how rooms are handled in your SocketIO events
    room = get_room_name(current_user.username, target_user.username)

    # Mark messages from target_user to current_user in this room as read
    if target_user and current_user:
        mark_all_messages_as_read_in_room(
            sender_username=target_user.username, 
            receiver_username=current_user.username, 
            room_name=room
        )
    
    # Fetch existing messages for this room
    # You might want to paginate this or limit the number of messages loaded initially
    messages = get_messages_for_room(room_name=room, limit=100) # Get last 100 messages
    # Messages are typically fetched in reverse chronological order, so reverse them for display
    messages.reverse()

    return render_template('chat/chat_room.html',
                           title=f"Chat with {target_user.username}",
                           target_user=target_user,
                           room_name=room,
                           chat_messages=messages)

@chat_bp.route('/upload_file', methods=['POST'])
@login_required
def upload_chat_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Ensure the UPLOAD_FOLDER exists
        upload_path = os.path.join(current_app.static_folder, UPLOAD_FOLDER)
        os.makedirs(upload_path, exist_ok=True)
        
        file_path = os.path.join(upload_path, filename)
        file.save(file_path)
        
        file_url = url_for('static', filename=f'{UPLOAD_FOLDER}/{filename}', _external=True)
        
        # Determine message_type from file extension
        ext = filename.rsplit('.', 1)[1].lower()
        message_type = 'text' # Default
        if ext in ['png', 'jpg', 'jpeg', 'gif']:
            message_type = 'image'
        elif ext == 'pdf':
            message_type = 'pdf'
        elif ext in ['mp4', 'webm', 'ogg']:
            message_type = 'video'
            
        return jsonify({"success": True, "file_url": file_url, "filename": filename, "message_type": message_type}), 200
    else:
        return jsonify({"error": "File type not allowed"}), 400

# Placeholder for a route that might list all active chats for a user, if needed later.
# @chat_bp.route('/')
# @login_required
# def list_chats():
#     # Logic to list chats
#     return render_template('chat/list_chats.html')