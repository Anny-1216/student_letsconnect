# app/socket_events.py
from . import socketio
from flask_socketio import emit, join_room, leave_room
from .models import save_message # Assuming you have a save_message function in models

# Placeholder for get_room_name function, will be defined properly later
def get_room_name(user1_sid, user2_sid):
    # Ensure consistent room naming by sorting usernames alphabetically
    # This ensures that both users generate the same room name regardless of who initiates
    # It could be user SIDs if they are stable and known, or usernames if they are unique identifiers for chat participants
    participants = sorted([str(user1_sid).lower(), str(user2_sid).lower()])
    return f"{participants[0]}_{participants[1]}"

@socketio.on('join')
def on_join(data):
    username = data.get('username') # Assuming username is sent by client
    room = data.get('room') # Assuming client sends a room name (e.g., based on who they are chatting with)
    if username and room:
        join_room(room)
        emit('status', {'msg': username + ' has entered the room.'}, room=room)

@socketio.on('message')
def on_message(data):
    sender = data.get('sender')
    receiver = data.get('receiver') # Need to know the receiver to determine the room
    content = data.get('content')
    
    if not sender or not receiver or not content:
        emit('error', {'msg': 'Missing sender, receiver, or content'})
        return

    # Determine the room name. This logic should be robust.
    # For 1-on-1 chat, a common practice is to sort usernames alphabetically and join them.
    # This ensures both users join the same room regardless of who initiated.
    room_participants = sorted([sender, receiver])
    room = f"{room_participants[0]}_{room_participants[1]}"

    # Save message to DB (ensure save_message can handle usernames or user IDs)
    # You might need to adjust save_message in models.py to accept usernames
    # or fetch user objects based on usernames before saving.
    message_id = save_message(sender_username=sender, receiver_username=receiver, content=content, room_name=room)
    
    if message_id:
        # Include timestamp and potentially message ID in the emitted message
        # The save_message function should ideally return the saved message object or dict
        # For now, we'll just re-emit the input data, assuming it's what the client expects.
        # You'll likely want to add a server-generated timestamp here.
        from datetime import datetime
        data_to_emit = {
            'sender': sender,
            'receiver': receiver,
            'content': content,
            'timestamp': datetime.utcnow().isoformat(),
            'room': room
        }
        emit('message', data_to_emit, room=room)
    else:
        emit('error', {'msg': 'Failed to save message.'})

@socketio.on('leave')
def on_leave(data):
    username = data.get('username')
    room = data.get('room')
    if username and room:
        leave_room(room)
        emit('status', {'msg': username + ' has left the room.'}, room=room)