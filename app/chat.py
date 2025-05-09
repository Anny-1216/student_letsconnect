# app/chat.py
from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import current_user, login_required
from .models import User, get_messages_for_room # Assuming User model and message functions are in models.py
from .socket_events import get_room_name # Import the get_room_name function

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/with/<target_username>', methods=['GET'])
@login_required
def start_chat_page(target_username):
    target_user = User.find_by_username(target_username)
    if not target_user:
        # Handle user not found, perhaps flash a message and redirect
        return redirect(url_for('matchmaking.browse_users')) # Or some error page

    if target_user.username == current_user.username:
        # Prevent user from chatting with themselves
        return redirect(url_for('matchmaking.browse_users'))

    # Determine the room name using the same logic as in socket_events
    # Ensure this is consistent with how rooms are handled in your SocketIO events
    room = get_room_name(current_user.username, target_user.username)
    
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

# Placeholder for a route that might list all active chats for a user, if needed later.
# @chat_bp.route('/')
# @login_required
# def list_chats():
#     # Logic to list chats
#     return render_template('chat/list_chats.html')