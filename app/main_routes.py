from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

# Create a Blueprint for the main routes
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # If user is already authenticated, redirect to the browse page
    if current_user.is_authenticated:
        return redirect(url_for('matchmaking.browse_users'))
    # Otherwise show the landing page
    return render_template('main/landing_page.html')

@main_bp.route('/home')
def home():
    # Redirect to index for now, can be changed if needed
    return redirect(url_for('main.index'))