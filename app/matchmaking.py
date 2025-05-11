# app/matchmaking.py
from flask import Blueprint, render_template, request, current_app
from flask_login import login_required, current_user
from .models import User, get_unread_message_count # Import the User model and get_unread_message_count

matchmaking_bp = Blueprint('matchmaking', __name__)

@matchmaking_bp.route('/browse', methods=['GET'])
@login_required
def browse_users():
    # Get filter criteria from request arguments
    role_filter = request.args.get('role')
    branch_filter = request.args.get('branch')

    query_filter = {}
    if role_filter:
        query_filter['role'] = role_filter
    if branch_filter:
        query_filter['branch'] = branch_filter
    
    # Logic for suggesting seniors to juniors
    # If the current user is a junior and no specific role is selected, show only seniors.
    if current_user.role == 'junior' and not role_filter:
        query_filter['role'] = 'senior'
    
    # Prevent users from seeing themselves in the list
    if 'username' not in query_filter: # if there is no specific username filter
        query_filter['username'] = {'$ne': current_user.username}
    elif query_filter['username'] == current_user.username: # if there is a username filter and it is the current user
        query_filter['username'] = {'$ne': current_user.username}


    users_to_display = User.find_all(query_filter)
    
    # For simplicity, we'll pass all roles and branches for filter dropdowns
    # In a larger app, you might get these from distinct DB queries
    all_roles = ['junior', 'senior'] 
    # Assuming branches are somewhat dynamic, get distinct branches from all users
    # This could be optimized if branches are fixed
    all_users_for_branches = User.find_all()
    all_branches = sorted(list(set(u.branch for u in all_users_for_branches if u.branch)))

    return render_template("matchmaking/browse_users.html", 
                           title="Browse Users", 
                           users=users_to_display,
                           all_roles=all_roles,
                           all_branches=all_branches,
                           current_filters={'role': role_filter, 'branch': branch_filter},
                           get_unread_message_count=get_unread_message_count) # Pass the function to the template context