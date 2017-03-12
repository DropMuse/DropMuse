from flask_login import UserMixin


class User(UserMixin):
    ''' User class for Flask-Login '''
    def __init__(self, user_id):
        self.id = user_id
        self.username = 'test_username'
