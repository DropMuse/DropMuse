from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators
from wtforms.fields.html5 import EmailField


class RegistrationForm(FlaskForm):
    username = StringField('Username', [
        validators.DataRequired(),
        validators.Length(min=3, max=25)
    ])
    email = EmailField('Email Address', [
        validators.Length(min=4, max=30),
        validators.DataRequired(),
        validators.Email()
    ])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')


class LoginForm(FlaskForm):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('Password', [validators.DataRequired()])


class PlaylistCreateForm(FlaskForm):
    title = StringField('Playlist Title', [
        validators.DataRequired(),
        validators.Length(min=3, max=25)
    ])
