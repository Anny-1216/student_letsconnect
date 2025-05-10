# app/auth.py
from flask import Blueprint
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from .forms import SignupForm, LoginForm, ProfileForm, RequestPasswordResetForm, ResetPasswordForm
from .models import User
from . import db # For direct db interaction if needed, though model methods are preferred
import os
import secrets
from werkzeug.utils import secure_filename
from datetime import datetime
from flask_mail import Message # Added Message
from . import mail # Added mail

auth_bp = Blueprint('auth', __name__)

def save_file(file, directory):
    """
    Save a file with a secure randomized name and return the filename
    """
    if file and file.filename:
        # Generate a random hex name to avoid filename conflicts
        random_hex = secrets.token_hex(8)
        _, file_extension = os.path.splitext(file.filename)
        filename = random_hex + file_extension
        
        # Create directory if it doesn't exist
        os.makedirs(directory, exist_ok=True)
        
        # Save the file
        file_path = os.path.join(directory, filename)
        file.save(file_path)
        
        return filename
    return None

def send_verification_email(user):
    token = user.generate_email_verification_token()
    msg = Message('Verify Your Email - LetsConnect',
                  sender=current_app.config['MAIL_USERNAME'],
                  recipients=[user.email])
    verify_url = url_for('auth.verify_email', token=token, _external=True)
    msg.body = f'''To verify your email, visit the following link:
{verify_url}

If you did not make this request then simply ignore this email.
'''
    mail.send(msg)

def send_password_reset_email(user):
    token = user.generate_password_reset_token()
    msg = Message('Password Reset Request - LetsConnect',
                  sender=current_app.config['MAIL_USERNAME'],
                  recipients=[user.email])
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    msg.body = f'''To reset your password, visit the following link:
{reset_url}

If you did not make this request then simply ignore this email.
'''
    mail.send(msg)

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('matchmaking.browse_users')) # Or a general home/dashboard
    form = SignupForm()
    if form.validate_on_submit():
        # Save the student document
        student_doc_filename = None
        if form.student_document.data:
            document_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'documents')
            student_doc_filename = save_file(form.student_document.data, document_dir)

        new_user = User(
            username=form.username.data,
            email=form.email.data,
            full_name=form.full_name.data,
            role=form.role.data,
            student_document=student_doc_filename,
            last_seen=datetime.utcnow()  # Set initial last seen
        )
        new_user.set_password(form.password.data)
        user_id = new_user.save() # Save user to MongoDB

        send_verification_email(new_user) # Send verification email

        flash('Account created successfully! Please check your email to verify your account.', 'info') # Changed flash message
        return redirect(url_for('auth.login')) # Redirect to login, user needs to verify first
    return render_template('auth/signup.html', title='Sign Up', form=form)

@auth_bp.route('/verify_email/<token>', methods=['GET'])
def verify_email(token):
    user = User.find_by_verification_token(token)
    if user:
        if user.verify_email_token(token):
            flash('Your email has been verified! You can now log in.', 'success')
        else:
            flash('Email verification link is invalid or has expired.', 'danger')
    else:
        flash('Email verification link is invalid or has expired.', 'danger')
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('matchmaking.browse_users')) # Or a general home/dashboard
    form = LoginForm()
    if form.validate_on_submit():
        user = User.find_by_email(form.email.data)
        if user and user.check_password(form.password.data):
            if not user.email_verified:
                flash('Please verify your email address first.', 'warning')
                return redirect(url_for('auth.login'))
            # Update last seen timestamp
            user.last_seen = datetime.utcnow()
            user.save()
            
            login_user(user, remember=form.remember.data)
            access_token = create_access_token(identity=user.id) # Use user.id (MongoDB ObjectId as string)
            flash('Login successful!', 'success')
            # Redirect to the page user was trying to access, or a default
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('matchmaking.browse_users'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('auth/login.html', title='Login', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    # Update last seen timestamp before logging out
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        current_user.save()
    
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(obj=current_user) # Pre-populate with current_user data
    if form.validate_on_submit():
        current_user.full_name = form.full_name.data
        current_user.branch = form.branch.data
        current_user.year = int(form.year.data) if form.year.data else current_user.year
        current_user.bio = form.bio.data
        
        # Handle skills
        if form.skills.data:
            current_user.skills = [skill.strip() for skill in form.skills.data.split(',') if skill.strip()]
        else:
            current_user.skills = []
            
        # Handle social links
        current_user.social_links = {
            "github": form.github.data if form.github.data else "",
            "linkedin": form.linkedin.data if form.linkedin.data else "",
            "twitter": form.twitter.data if form.twitter.data else ""
        }
        
        # REMOVE PROFILE PHOTO LOGIC FROM HERE
        # Profile photo is now handled by the /upload_profile_photo route
        
        # Update last seen timestamp
        current_user.last_seen = datetime.utcnow()
        
        # Save user data
        current_user.save()
        
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('auth.profile'))  # Redirect back to profile to see changes
    
    elif request.method == 'GET':
        # Populate form fields
        form.full_name.data = current_user.full_name
        form.branch.data = current_user.branch
        form.year.data = str(current_user.year) if current_user.year is not None else ''
        form.bio.data = current_user.bio
        form.skills.data = ", ".join(current_user.skills) if current_user.skills else ""
        
        if current_user.social_links:
            form.github.data = current_user.social_links.get("github", "")
            form.linkedin.data = current_user.social_links.get("linkedin", "")
            form.twitter.data = current_user.social_links.get("twitter", "")
        
    return render_template('auth/profile.html', title='Profile', form=form)

@auth_bp.route('/upload_profile_photo', methods=['POST'])
@login_required
def upload_profile_photo():
    if 'profile_photo' not in request.files:
        flash('No file selected', 'danger')
        return redirect(url_for('auth.profile'))
        
    profile_photo = request.files['profile_photo']
    
    if profile_photo.filename == '':
        flash('No file selected', 'danger')
        return redirect(url_for('auth.profile'))
    
    # Check if the file is allowed
    allowed_extensions = {'jpg', 'jpeg', 'png'}
    file_ext = os.path.splitext(profile_photo.filename)[1].lower()[1:]  # Remove the dot
    
    if file_ext not in allowed_extensions:
        flash('Only JPG, JPEG, and PNG files are allowed', 'danger')
        return redirect(url_for('auth.profile'))
    
    try:
        # Create uploads directory if it doesn't exist
        profile_pics_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'profile_pics')
        os.makedirs(profile_pics_dir, exist_ok=True)
        
        # Generate a unique filename
        unique_filename = secrets.token_hex(8) + '.' + file_ext
        file_path = os.path.join(profile_pics_dir, unique_filename)
        
        # Save the file
        profile_photo.save(file_path)
        
        # Update the user's profile with the new filename
        current_user.profile_photo = unique_filename
        current_user.save()
        
        flash('Profile photo updated successfully!', 'success')
    except Exception as e:
        print(f"Error uploading profile photo: {e}")
        flash('An error occurred while uploading your photo. Please try again.', 'danger')
    
    return redirect(url_for('auth.profile'))

@auth_bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('matchmaking.browse_users'))
    form = RequestPasswordResetForm()
    if form.validate_on_submit():
        user = User.find_by_email(form.email.data)
        if user:
            send_password_reset_email(user)
            flash('An email has been sent with instructions to reset your password.', 'info')
        else:
            # Flash message even if user doesn't exist to prevent email enumeration
            flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/request_reset_password.html', title='Request Password Reset', form=form)

@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('matchmaking.browse_users'))
    user = User.find_by_password_reset_token(token)
    if not user or not user.verify_password_reset_token(token):
        flash('The password reset link is invalid or has expired.', 'warning')
        return redirect(url_for('auth.reset_password_request'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        user.password_reset_token = None # Clear the token
        user.password_reset_token_expiry = None
        user.save()
        flash('Your password has been reset successfully! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', title='Reset Password', form=form, token=token)

# Create a before_request handler to update last_seen for authenticated users
@auth_bp.before_app_request
def update_last_seen():
    if current_user.is_authenticated:
        # Only update every few minutes to avoid excessive database writes
        if (not current_user.last_seen or 
            (datetime.utcnow() - current_user.last_seen).total_seconds() > 300):  # Update every 5 minutes
            current_user.last_seen = datetime.utcnow()
            current_user.save()

# The rest of your routes remain unchanged