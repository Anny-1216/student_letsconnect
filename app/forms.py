from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, TextAreaField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from .models import User # To check for existing username/email

class SignupForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    full_name = StringField('Full Name',
                           validators=[DataRequired(), Length(min=2, max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[('junior', 'Junior'), ('senior', 'Senior')],
                       validators=[DataRequired()])
    student_document = FileField('Student ID Card/Document', 
                               validators=[FileRequired(), 
                                           FileAllowed(['jpg', 'png', 'pdf'], 'Images and PDF only!')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.find_by_username(username.data)
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.find_by_email(email.data)
        if user:
            raise ValidationError('That email is already registered. Please choose a different one or login.')

class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RequestPasswordResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.find_by_email(email.data)
        if not user:
            raise ValidationError('There is no account with that email. You must register first.')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

class ProfileForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=50)])
    branch = SelectField('Branch',
                         choices=[
                             ('', 'Select Branch'),
                             ("Computer Engineering", "Computer Engineering"),
                             ("Information Technology", "Information Technology"),
                             ("Electronics & Telecommunication Engineering", "Electronics & Telecommunication Engineering"),
                             ("Mechanical Engineering", "Mechanical Engineering"),
                             ("Civil Engineering", "Civil Engineering"),
                             ("Artificial Intelligence & Machine Learning (AIML)", "Artificial Intelligence & Machine Learning (AIML)"),
                             ("Artificial Intelligence & Data Science (AIDS)", "Artificial Intelligence & Data Science (AIDS)"),
                             ("Electronics & Computer Engineering (ECE)", "Electronics & Computer Engineering (ECE)"),
                             ("Internet of Things (IOT)", "Internet of Things (IOT)")
                         ],
                         default='',
                         validators=[]) # Optional: Add DataRequired() if branch is mandatory
    year = SelectField('Year', 
                       choices=[('', 'Select Year'), ('1', '1st Year'), ('2', '2nd Year'), ('3', '3rd Year'), ('4', '4th Year')],
                       default='',  # Default to the 'Select Year' option
                       validators=[]) # DataRequired removed, can be added if year is mandatory
    bio = TextAreaField('Bio', validators=[Length(max=200)])
    skills = StringField('Skills (comma separated)', validators=[Length(max=200)])
    github = StringField('GitHub URL', validators=[Length(max=100)])
    linkedin = StringField('LinkedIn URL', validators=[Length(max=100)])
    twitter = StringField('Twitter URL', validators=[Length(max=100)])
    # profile_photo field removed since it's now handled separately
    submit = SubmitField('Update Profile')
