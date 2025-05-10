# app/connections.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from bson import ObjectId
from datetime import datetime # Added datetime for potential future use with rejections

from .models import User, create_connection_request, get_pending_connection_requests, update_connection_request_status, get_user_connections, are_users_connected, get_connection_request_by_id, get_connection_status_between_users
from . import db

connections_bp = Blueprint('connections', __name__)

@connections_bp.route('/send_request/<target_username>', methods=['POST'])
@login_required
def send_connection_request_route(target_username): # Renamed to avoid conflict with model function
    target_user = User.find_by_username(target_username)
    if not target_user:
        flash('User not found.', 'danger')
        return redirect(request.referrer or url_for('matchmaking.browse_users'))

    if target_user.id == current_user.id:
        flash('You cannot connect with yourself.', 'warning')
        return redirect(request.referrer or url_for('matchmaking.browse_users'))

    sender_oid = ObjectId(current_user.id)
    receiver_oid = ObjectId(target_user.id)

    # Check current status before attempting to create a new request
    status = get_connection_status_between_users(sender_oid, receiver_oid)
    if status == "connected":
        flash(f'You are already connected with {target_user.username}.', 'info')
        return redirect(request.referrer or url_for('matchmaking.browse_users'))
    if status == "pending_sent":
        flash(f'You already have a pending request sent to {target_user.username}.', 'info')
        return redirect(request.referrer or url_for('matchmaking.browse_users'))
    # If status is "pending_received", they should accept it, not send a new one.
    # If status is "rejected_by_them" or "rejected_by_you", we might allow a new request or have a cooldown.
    # For now, create_connection_request in models.py handles the check for existing pending/accepted.

    request_created = create_connection_request(sender_id=sender_oid, receiver_id=receiver_oid)

    if request_created:
        flash(f'Connection request sent to {target_user.username}.', 'success')
    else:
        flash(f'Could not send connection request. You might already have a pending/accepted request with {target_user.username}, or they may have rejected a previous request recently.', 'warning')
    
    return redirect(request.referrer or url_for('matchmaking.browse_users'))

@connections_bp.route('/requests', methods=['GET'])
@login_required
def view_pending_requests():
    user_oid = ObjectId(current_user.id)
    pending_requests = get_pending_connection_requests(user_id=user_oid)
    return render_template('connections/pending_requests.html', title="Connection Requests", requests=pending_requests)

@connections_bp.route('/respond_request/<request_id>/<action>', methods=['POST'])
@login_required
def respond_to_request(request_id, action):
    if action not in ['accept', 'reject']:
        flash('Invalid action.', 'danger')
        return redirect(url_for('.view_pending_requests'))

    user_oid_making_change = ObjectId(current_user.id)
    
    # The status to set in the DB should be past tense, e.g., 'accepted', 'rejected'
    status_to_set = f'{action}ed' 
    updated_request = update_connection_request_status(request_id, status_to_set, user_oid_making_change)

    if updated_request == "unauthorized":
        flash('You are not authorized to respond to this request.', 'danger')
    elif updated_request == "not_pending":
        flash('This request is no longer pending.', 'warning')
    elif updated_request:
        flash(f'Request {status_to_set} successfully.', 'success')
    else:
        flash('Failed to update request status or request not found.', 'danger')
        
    return redirect(url_for('.view_pending_requests'))

@connections_bp.route('/my_connections', methods=['GET'])
@login_required
def my_connections_page(): # Renamed to avoid conflict
    user_oid = ObjectId(current_user.id)
    connections = get_user_connections(user_id=user_oid) 
    return render_template(
        'connections/my_connections.html',
        title="My Connections",
        connections=connections,
        current_user_obj=current_user,
        get_connection_status_between_users=get_connection_status_between_users
    )

@connections_bp.route('/remove_connection/<target_username>', methods=['POST'])
@login_required
def remove_connection(target_username):
    target_user = User.find_by_username(target_username)
    if not target_user:
        flash('User not found.', 'danger')
        return redirect(request.referrer or url_for('.my_connections_page'))

    current_user_oid = ObjectId(current_user.id)
    target_user_oid = ObjectId(target_user.id)
    
    if not are_users_connected(current_user_oid, target_user_oid):
        flash(f'You are not connected with {target_username}.', 'warning')
        return redirect(request.referrer or url_for('.my_connections_page'))

    # Remove from connections lists
    db.users.update_one({"_id": current_user_oid}, {"$pull": {"connections": target_user_oid}})
    db.users.update_one({"_id": target_user_oid}, {"$pull": {"connections": current_user_oid}})
    
    # Optionally, update the status of the original connection_request to "disconnected" or similar
    # This helps in not showing it as "accepted" anymore if you query connection_requests directly
    db.connection_requests.update_many(
        {
            "$or": [
                {"sender_id": current_user_oid, "receiver_id": target_user_oid, "status": "accepted"},
                {"sender_id": target_user_oid, "receiver_id": current_user_oid, "status": "accepted"}
            ]
        },
        {"$set": {"status": "disconnected", "updated_at": datetime.utcnow()}}
    )

    flash(f'You have disconnected from {target_username}.', 'success')
    return redirect(request.referrer or url_for('.my_connections_page'))
