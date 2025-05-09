# app/matchmaking.py
from flask import Blueprint, render_template
from flask_login import login_required

matchmaking_bp = Blueprint('matchmaking', __name__)

@matchmaking_bp.route('/browse')
@login_required
def browse_users():
    # This is a placeholder. Actual implementation will be in Phase 3.
    # For now, it just confirms the user is logged in and can reach this page.
    return render_template("matchmaking/browse_placeholder.html", title="Browse Users")