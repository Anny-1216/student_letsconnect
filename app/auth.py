# app/auth.py
from flask import Blueprint
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from .forms import SignupForm, LoginForm, ProfileForm
from .models import User
from . import db # For direct db interaction if needed, though model methods are preferred

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('matchmaking.browse_users')) # Or a general home/dashboard
    form = SignupForm()
    if form.validate_on_submit():
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            role=form.role.data
        )
        new_user.set_password(form.password.data)
        user_id = new_user.save() # Save user to MongoDB

        # Log in the user immediately after signup
        # Need to fetch the user object again to get the ID in the right format for flask-login
        # or ensure .save() returns/sets the id in a way load_user can use.
        # For now, let's assume load_user works with the string ID from new_user.id
        login_user(new_user)

        flash('Account created successfully! Please complete your profile.', 'success')
        return redirect(url_for('auth.profile'))
    return render_template('auth/signup.html', title='Sign Up', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('matchmaking.browse_users')) # Or a general home/dashboard
    form = LoginForm()
    if form.validate_on_submit():
        user = User.find_by_email(form.email.data)
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            access_token = create_access_token(identity=user.id) # Use user.id (MongoDB ObjectId as string)
            flash('Login successful!', 'success')
            # Redirect to the page user was trying to access, or a default
            next_page = request.args.get('next')
            # Consider returning the token in the response if the client is a SPA
            # For server-rendered, session is primary, token can be stored if needed for API calls
            response_data = {'message': 'Login successful', 'access_token': access_token}
            # For now, simple redirect
            return redirect(next_page) if next_page else redirect(url_for('matchmaking.browse_users'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('auth/login.html', title='Login', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(obj=current_user) # Pre-populate with current_user data
    if form.validate_on_submit():
        current_user.branch = form.branch.data
        # Handle year: if it's an empty string (from 'Select Year'), store None or keep existing.
        current_user.year = int(form.year.data) if form.year.data else current_user.year # Or None
        current_user.bio = form.bio.data
        current_user.save() # Assumes current_user is a User object from models.py
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('matchmaking.browse_users')) # Or wherever appropriate
    elif request.method == 'GET':
        # Ensure form fields are populated correctly, especially SelectField for 'year'
        form.branch.data = current_user.branch
        form.year.data = str(current_user.year) if current_user.year is not None else ''
        form.bio.data = current_user.bio
        
    return render_template('auth/profile.html', title='Profile', form=form)

# Optional: A route to get a new JWT token if needed, e.g., if session expires but user has valid refresh token
# This is more advanced and depends on how you manage JWT lifecycles.
# For now, JWT is created at login and primarily for potential API usage.

# User loader for Flask-Login is in models.py