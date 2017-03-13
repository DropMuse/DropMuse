from flask_login import UserMixin


class User(UserMixin):
    ''' User class for Flask-Login '''
    def __init__(self, user_id, username=None):
        self.id = user_id
        self.username = username
