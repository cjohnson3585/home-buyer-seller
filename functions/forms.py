"""Forms for the bull application."""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    """Form class for user login."""
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])

class UserSignupForm(FlaskForm):
    """Form class for poster login."""
    username = StringField('username', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired()])
    phonenumber = StringField('phonenumber')
    firstname = StringField('firstname')
    lastname = StringField('lastname')
    city = StringField('city')
    state = StringField('state')
    password = PasswordField('password', validators=[DataRequired()])


class JobPostingForm(FlaskForm):
    """Form class for poster job posting information."""
    username = StringField('username', validators=[DataRequired()])
    jobid = StringField('jobid', validators=[DataRequired()])
    contactemail = StringField('contactemail', validators=[DataRequired()])
    contactphone = StringField('contactphone', validators=[DataRequired()])
    website = StringField('website', validators=[DataRequired()])
    companydescription = StringField('companydescription', validators=[DataRequired()])
    jobtype = StringField('jobtype', validators=[DataRequired()])
    jobdescription = StringField('jobdescription', validators=[DataRequired()])
    payoffered = StringField('payoffered', validators=[DataRequired()])
    jobduration = StringField('jobduration', validators=[DataRequired()])
    startdate = StringField('startdate', validators=[DataRequired()])
    longdescription = StringField('longdescritpion', validators=[DataRequired()])
