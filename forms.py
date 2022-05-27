from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateTimeField
from wtforms.validators import InputRequired


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])

class UserReportsForm(FlaskForm):
    start_date = DateTimeField('Start date', validators=[InputRequired()])
    end_date = DateTimeField('End date', validators=[InputRequired()])

class VehicleReportsForm(FlaskForm):
    start_date = DateTimeField('Start date', validators=[InputRequired()])
    end_date = DateTimeField('End date', validators=[InputRequired()])

class AddUserForm(FlaskForm):
    username = StringField('Username', validators = [InputRequired()])
    phone = StringField('Phone', validators=[InputRequired()])

class ProfileForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    phone = StringField('Phone', validators=[InputRequired()])
    password = PasswordField('Password',validators=[InputRequired()])
