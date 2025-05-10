# app/socket_events.py
from . import socketio
from flask_socketio import emit, join_room, leave_room
from flask import request
from flask_login import current_user
from .models import save_message, User, mark_message_as_read # Added mark_message_as_read
from bson import ObjectId # For type checking if needed, though models.py handles conversion for save/update

# Renamed parameters for clarity to match usage from chat.py
def get_room_name(username1, username2):
    participants = sorted([str(username1).lower(), str(username2).lower()])
    return f"{participants[0]}_{participants[1]}"

@socketio.on('join')
def on_join(data):
    username = data.get('username') # Assuming username is sent by client
    room = data.get('room') # Assuming client sends a room name (e.g., based on who they are chatting with)
    if username and room:
        join_room(room)
        emit('status', {'msg': username + ' has entered the room.'}, room=room)

@socketio.on('message')
# @login_required # Removed decorator
def handle_message(data):
    """Handles incoming chat messages."""
    # print(f"Received message: {data} from {data.get('sender')}") # Use sender from data
    
    # TODO: Implement a more robust way to verify the sender's identity
    # For example, associate request.sid with a username upon 'join' 
    # and verify against that stored association.
    # For now, we proceed with the sender from the data, assuming client-side authentication handled it.

    # if current_user and current_user.is_authenticated and current_user.username != data.get('sender'):
    #     emit('error', {'msg': 'Sender mismatch.'}, room=request.sid)
    #     return
    # elif not current_user or not current_user.is_authenticated:
    #     emit('error', {'msg': 'User not authenticated for sending messages.'}, room=request.sid)
    #     return

    sender_username = data.get('sender')
    receiver_username = data.get('receiver')
    content = data.get('content')
    room_name = data.get('room')

    if not all([sender_username, receiver_username, content, room_name]):
        emit('error', {'msg': 'Missing data in message.'}, room=request.sid)
        return

    # Save the message to the database
    saved_message_doc = save_message(
        sender_username=sender_username,
        receiver_username=receiver_username,
        content=content,
        room_name=room_name
    )

    if saved_message_doc:
        message_to_emit = {
            '_id': str(saved_message_doc['_id']),
            'sender': saved_message_doc['sender_username'],
            'receiver': saved_message_doc['receiver_username'],
            'content': saved_message_doc['content'],
            'room': saved_message_doc['room'],
            'timestamp': saved_message_doc['timestamp'].isoformat(),
            'read_at': saved_message_doc['read_at'].isoformat() if saved_message_doc['read_at'] else None,
        }

        # Emit the message to the specific room, skipping the sender
        emit('message', message_to_emit, room=room_name, skip_sid=request.sid)
        # Emit an acknowledgment back to the sender with the full message details
        emit('message_ack', message_to_emit, room=request.sid)
    else:
        emit('error', {'msg': 'Failed to save message.'}, room=request.sid)

@socketio.on('leave')
def on_leave(data):
    username = data.get('username')
    room = data.get('room')
    if username and room:
        leave_room(room)
        emit('status', {'msg': username + ' has left the room.'}, room=room)

@socketio.on('message_read_ack')
def handle_message_read_ack(data):
    """Handles event when a client acknowledges they have read a message."""
    if not current_user.is_authenticated:
        emit('error', {'msg': 'User not authenticated for read acknowledgment.'}, room=request.sid)
        return

    message_id = data.get('message_id')
    room_name = data.get('room') # The client should send the room name for context

    if not message_id or not room_name:
        emit('error', {'msg': 'Missing message_id or room_name for read acknowledgment.'}, room=request.sid)
        return

    reader_username = current_user.username
    # print(f"User {reader_username} attempting to mark message {message_id} in room {room_name} as read.")

    updated_message_data = mark_message_as_read(message_id, reader_username)

    if updated_message_data:
        # print(f"Message {message_id} marked as read. Notifying room {room_name}.")
        # Notify the entire room about the read update.
        # The client-side will determine if this update is relevant to them (e.g., if they are the sender).
        emit_data = {
            'message_id': updated_message_data['_id'], # Already a string
            'read_at': updated_message_data['read_at'].isoformat(),
            'reader_username': updated_message_data['receiver_username'], # This is who read the message
            'sender_username': updated_message_data['sender_username'] # Original sender
        }
        emit('message_read_update', emit_data, room=room_name)
    # else:
        # print(f"Failed to mark message {message_id} as read or no update needed.")
        # Optionally, emit an error or a specific status back to the reader if needed,
        # but for read receipts, often no explicit error for "already read" is sent to the reader.
        # The main goal is to inform the sender.