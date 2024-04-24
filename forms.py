from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField
from wtforms.validators import InputRequired, Email, EqualTo, Length, ValidationError

from models import User


    
class SignUp(FlaskForm):
    """Sign up form"""
    
    first_name = StringField("First Name", validators=[InputRequired()])
    last_name = StringField("Last Name", validators=[InputRequired()])
    email = EmailField("Email", validators=[InputRequired(), Email(message='Not a valid email')])
   
    def validate_email(form, field):
        #if found, raise error
        email = field.data
        if User.query.filter(User.email==email).all(): 
            raise ValidationError('Username is already taken!')
    
    password = PasswordField("Password", 
                           validators=[
                               InputRequired(),
                               Length(min=- 6, message='Must be at least 6 characters!'), 
                               EqualTo('confirm', message='Passwords must match!')
                               ]
                           )
    confirm = PasswordField("Confirm Password")
    
class LoginForm(FlaskForm):
    """Login Form"""
    
    email = EmailField("Email", validators=[InputRequired(), Email(message='Not a valid email')])
    password = PasswordField("Password", validators=[InputRequired()])