from flask_login import UserMixin


class User(UserMixin):
    ''' User class for Flask-Login '''
    def __init__(self, user_id, username=None):
        self.id = user_id
        self.username = username


class Playlist(object):
    ''' Playlist object representation '''
    def __init__(self, playlist_id, title=None, duration=0, count=0):
        self.id = playlist_id
        self.title = title
        self.duration = duration
        self.count = count
