from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from .models import User # To check for existing username/email

class SignupForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[('junior', 'Junior'), ('senior', 'Senior')],
                       validators=[DataRequired()])
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

class ProfileForm(FlaskForm):
    branch = StringField('Branch', validators=[Length(max=50)])
    # Allow '' as a valid choice for 'Select Year', make it not strictly DataRequired
    year = SelectField('Year', 
                       choices=[('', 'Select Year'), ('1', '1st Year'), ('2', '2nd Year'), ('3', '3rd Year'), ('4', '4th Year'), ('5', '5th Year+')],
                       default='',  # Default to the 'Select Year' option
                       validators=[]) # DataRequired removed, can be added if year is mandatory
    bio = TextAreaField('Bio', validators=[Length(max=200)])
    submit = SubmitField('Update Profile')
