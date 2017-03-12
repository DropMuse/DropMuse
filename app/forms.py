from wtforms import Form, StringField, PasswordField, validators
from wtforms.fields.html5 import EmailField


class RegistrationForm(Form):
    username = StringField('Username', [
        validators.DataRequired(),
        validators.Length(min=4, max=25)
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


class LoginForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('Password', [validators.DataRequired()])
