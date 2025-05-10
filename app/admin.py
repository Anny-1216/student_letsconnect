# app/admin.py
from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from functools import wraps
from .models import User
from . import db # Assuming db is your MongoDB instance from __init__.py
from bson import ObjectId

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Decorator to ensure user is an admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    users = User.find_all() # Fetch all users
    return render_template('admin/dashboard.html', title='Admin Dashboard', users=users)

@admin_bp.route('/users/<user_id>/verify_document/<action>', methods=['POST'])
@login_required
@admin_required
def verify_document(user_id, action):
    user = User.find_by_username(user_id) # Assuming user_id is username for simplicity, or use ObjectId if it is id
    if not user:
        user_data = db.users.find_one({"_id": ObjectId(user_id)})
        if user_data:
            user = User(
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
                is_admin=user_data.get('is_admin', False),
                student_document_verified=user_data.get('student_document_verified', False)
            )
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('admin.dashboard'))

    if action == 'approve':
        user.student_document_verified = True
        flash(f'Document for {user.username} approved.', 'success')
    elif action == 'reject':
        user.student_document_verified = False # Or some other status like 'rejected'
        # Optionally, you might want to clear the student_document field or notify the user
        flash(f'Document for {user.username} rejected.', 'warning')
    else:
        flash('Invalid action.', 'danger')

    user.save()
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/users/<user_id>/toggle_activation', methods=['POST'])
@login_required
@admin_required
def toggle_activation(user_id):
    user = User.find_by_username(user_id) # Assuming user_id is username for simplicity, or use ObjectId if it is id
    if not user:
        user_data = db.users.find_one({"_id": ObjectId(user_id)})
        if user_data:
            user = User(
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
                is_admin=user_data.get('is_admin', False),
                student_document_verified=user_data.get('student_document_verified', False)
            )
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('admin.dashboard'))

    user.is_active = not user.is_active
    user.save()
    status = "activated" if user.is_active else "deactivated"
    flash(f'User {user.username} has been {status}.', 'success')
    return redirect(url_for('admin.dashboard'))
